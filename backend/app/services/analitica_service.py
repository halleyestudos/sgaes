from __future__ import annotations

from collections import defaultdict
from statistics import mean

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aluno import Aluno
from app.models.escola import Escola
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario


async def estatisticas_rede(db: AsyncSession, rede_id: int) -> dict:
    escolas = await db.scalar(select(func.count()).select_from(Escola).where(Escola.rede_id == rede_id, Escola.ativo.is_(True)))
    turmas = await db.scalar(select(func.count()).select_from(Turma).where(Turma.rede_id == rede_id, Turma.ativa.is_(True)))
    alunos = await db.scalar(select(func.count()).select_from(Aluno).where(Aluno.rede_id == rede_id, Aluno.ativo.is_(True)))
    professores = await db.scalar(
        select(func.count()).select_from(Usuario).where(Usuario.rede_id == rede_id, Usuario.perfil == "professor")
    )
    presencas = await db.scalar(
        select(func.count()).select_from(Frequencia).where(Frequencia.rede_id == rede_id, Frequencia.presente.is_(True))
    )
    total_freq = await db.scalar(select(func.count()).select_from(Frequencia).where(Frequencia.rede_id == rede_id))
    percentual = round((presencas or 0) * 100 / total_freq, 1) if total_freq else None
    return {
        "escolas_ativas": escolas or 0,
        "turmas_ativas": turmas or 0,
        "alunos_ativos": alunos or 0,
        "professores": professores or 0,
        "frequencia_media_rede": percentual,
    }


async def correlacao_deslocamento_faltas(db: AsyncSession, rede_id: int) -> dict:
    faltas_expr = func.sum(case((Frequencia.presente.is_(False), 1), else_=0))
    stmt = (
        select(
            Aluno.id,
            Aluno.nome,
            Aluno.bairro,
            Aluno.distancia_metros,
            Aluno.tempo_deslocamento_min,
            Aluno.modal_transporte,
            func.count(Frequencia.id).label("registros"),
            faltas_expr.label("faltas"),
        )
        .outerjoin(Frequencia, Frequencia.aluno_id == Aluno.id)
        .where(Aluno.rede_id == rede_id, Aluno.ativo.is_(True), Aluno.distancia_metros.is_not(None))
        .group_by(Aluno.id)
    )
    rows = (await db.execute(stmt)).all()
    itens = []
    for row in rows:
        registros = int(row.registros or 0)
        faltas = int(row.faltas or 0)
        percentual_faltas = round(faltas * 100 / registros, 1) if registros else 0.0
        itens.append(
            {
                "aluno_id": row.id,
                "nome": row.nome,
                "bairro": row.bairro,
                "distancia_metros": float(row.distancia_metros) if row.distancia_metros is not None else None,
                "tempo_deslocamento_min": row.tempo_deslocamento_min,
                "modal_transporte": row.modal_transporte,
                "registros": registros,
                "faltas": faltas,
                "percentual_faltas": percentual_faltas,
            }
        )

    correlacao = None
    pares = [(i["distancia_metros"], i["percentual_faltas"]) for i in itens if i["distancia_metros"] is not None]
    if len(pares) >= 2:
        xs = [p[0] for p in pares]
        ys = [p[1] for p in pares]
        mx, my = mean(xs), mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        correlacao = round(num / den, 3) if den else None

    return {"amostra": len(itens), "correlacao_pearson_distancia_faltas": correlacao, "itens": itens}


async def ambiente_por_bairro(db: AsyncSession, rede_id: int, bairro: str | None = None) -> list[dict]:
    presencas_expr = func.sum(case((Frequencia.presente.is_(True), 1), else_=0))
    stmt = (
        select(
            Aluno,
            Turma.turno,
            Turma.oferece_merenda,
            Turma.apoio_pedagogico,
            Usuario.nome.label("professor_nome"),
            func.count(Frequencia.id).label("registros"),
            presencas_expr.label("presencas"),
        )
        .outerjoin(Matricula, (Matricula.aluno_id == Aluno.id) & (Matricula.status == "ativa"))
        .outerjoin(Turma, Turma.id == Matricula.turma_id)
        .outerjoin(Usuario, Usuario.id == Turma.professor_id)
        .outerjoin(Frequencia, Frequencia.aluno_id == Aluno.id)
        .where(Aluno.rede_id == rede_id, Aluno.ativo.is_(True), Aluno.bairro.is_not(None))
        .group_by(Aluno.id, Turma.turno, Turma.oferece_merenda, Turma.apoio_pedagogico, Usuario.nome)
    )
    if bairro:
        stmt = stmt.where(Aluno.bairro.ilike(bairro))

    rows = (await db.execute(stmt)).all()
    por_bairro: dict[str, list] = defaultdict(list)
    for row in rows:
        aluno = row[0]
        registros = int(row.registros or 0)
        presencas = int(row.presencas or 0)
        por_bairro[aluno.bairro or "Sem bairro"].append(
            {
                "aluno_id": aluno.id,
                "nome": aluno.nome,
                "turno": row.turno,
                "professor": row.professor_nome,
                "oferece_merenda": row.oferece_merenda,
                "apoio_pedagogico": row.apoio_pedagogico,
                "acesso_internet": aluno.acesso_internet,
                "acesso_materiais": aluno.acesso_materiais,
                "modal_transporte": aluno.modal_transporte,
                "tempo_deslocamento_min": aluno.tempo_deslocamento_min,
                "percentual_frequencia": round(presencas * 100 / registros, 1) if registros else None,
            }
        )

    resultado = []
    for nome_bairro, alunos in sorted(por_bairro.items()):
        freqs = [a["percentual_frequencia"] for a in alunos if a["percentual_frequencia"] is not None]
        resultado.append(
            {
                "bairro": nome_bairro,
                "alunos": len(alunos),
                "frequencia_media": round(mean(freqs), 1) if freqs else None,
                "com_internet": sum(1 for a in alunos if a["acesso_internet"]),
                "com_materiais": sum(1 for a in alunos if a["acesso_materiais"]),
                "detalhes": alunos,
            }
        )
    return resultado
