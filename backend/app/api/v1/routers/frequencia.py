from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_FREQUENCIA, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.alerta_frequencia import AlertaFrequencia
from app.models.aluno import Aluno
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.schemas.frequencia import AlertaRead, ChamadaCreate, ChamadaDiaItem, ChamadaRead, FrequenciaConsolidada
from app.services.alerta_service import calcular_nivel_alerta

router = APIRouter(prefix="/frequencia", tags=["frequencia"])


@router.post("/chamada", response_model=list[ChamadaRead], status_code=status.HTTP_200_OK, summary="Registrar chamada", description="Registra ou atualiza a chamada inteira de uma turma de forma idempotente.", responses={200: {"description": "Chamada gravada e alertas recalculados."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}, 404: {"description": "Turma não encontrada."}})
async def registrar_chamada(payload: ChamadaCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_FREQUENCIA)), db: AsyncSession = Depends(get_db)) -> list[Frequencia]:
    await get_owned(db, Turma, payload.turma_id, usuario, "Turma não encontrada.")

    aluno_ids = {item.aluno_id for item in payload.itens}
    matriculas = (await db.execute(select(Matricula).where(Matricula.turma_id == payload.turma_id, Matricula.status == "ATIVA", Matricula.aluno_id.in_(aluno_ids), Matricula.rede_id == usuario.rede_id))).scalars().all()
    matriculados = {matricula.aluno_id: matricula for matricula in matriculas}
    if aluno_ids != set(matriculados):
        raise HTTPException(status_code=400, detail="Todos os alunos da chamada devem estar matriculados na turma.")

    registros: list[Frequencia] = []
    for item in payload.itens:
        registro = (await db.execute(select(Frequencia).where(Frequencia.turma_id == payload.turma_id, Frequencia.aluno_id == item.aluno_id, Frequencia.data == payload.data, Frequencia.ordem == payload.ordem, Frequencia.rede_id == usuario.rede_id))).scalar_one_or_none()
        if registro is None:
            registro = Frequencia(rede_id=usuario.rede_id, turma_id=payload.turma_id, aluno_id=item.aluno_id, data=payload.data, ordem=payload.ordem)
            db.add(registro)
        registro.presente = item.presente
        registro.observacao = item.observacao
        registros.append(registro)

    await db.flush()
    for aluno_id, matricula in matriculados.items():
        total, presentes = (await db.execute(select(func.count(Frequencia.id), func.count(Frequencia.id).filter(Frequencia.presente.is_(True))).where(Frequencia.aluno_id == aluno_id, Frequencia.turma_id == payload.turma_id, Frequencia.rede_id == usuario.rede_id))).one()
        nivel = calcular_nivel_alerta(presentes, total)
        alerta = (await db.execute(select(AlertaFrequencia).where(AlertaFrequencia.aluno_id == aluno_id, AlertaFrequencia.ano_letivo_id == matricula.ano_letivo_id, AlertaFrequencia.rede_id == usuario.rede_id))).scalar_one_or_none()
        if nivel.nivel is None:
            if alerta is not None:
                alerta.resolvido = True
        elif alerta is None:
            db.add(AlertaFrequencia(rede_id=usuario.rede_id, aluno_id=aluno_id, ano_letivo_id=matricula.ano_letivo_id, nivel=nivel.nivel, percentual=nivel.percentual))
        else:
            alerta.nivel = nivel.nivel
            alerta.percentual = nivel.percentual
            alerta.resolvido = False

    await db.commit()
    return registros


@router.get(
    "/turma/{turma_id}/chamada",
    response_model=list[ChamadaDiaItem],
    summary="Obter chamada do dia",
    description="Retorna a situação de presença/falta dos alunos matriculados para a data e ordem informadas.",
    responses={200: {"description": "Chamada do dia."}, 401: {"description": "Token inválido ou ausente."}, 404: {"description": "Turma não encontrada."}},
)
async def obter_chamada_do_dia(
    turma_id: int,
    data: date = Query(...),
    ordem: int = Query(1, ge=1),
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChamadaDiaItem]:
    await get_owned(db, Turma, turma_id, usuario, "Turma não encontrada.")
    alunos = (
        await db.execute(
            select(Aluno.id, Aluno.nome)
            .join(Matricula, Matricula.aluno_id == Aluno.id)
            .where(Matricula.turma_id == turma_id, Matricula.status == "ATIVA", Matricula.rede_id == usuario.rede_id)
            .order_by(Aluno.nome)
        )
    ).all()
    registros = (
        await db.execute(
            select(Frequencia).where(
                Frequencia.turma_id == turma_id,
                Frequencia.data == data,
                Frequencia.ordem == ordem,
                Frequencia.rede_id == usuario.rede_id,
            )
        )
    ).scalars().all()
    por_aluno = {item.aluno_id: item for item in registros}
    return [
        ChamadaDiaItem(
            aluno_id=aluno_id,
            nome=nome,
            presente=por_aluno[aluno_id].presente if aluno_id in por_aluno else True,
            observacao=por_aluno[aluno_id].observacao if aluno_id in por_aluno else None,
            registrada=aluno_id in por_aluno,
        )
        for aluno_id, nome in alunos
    ]


@router.get("/turma/{turma_id}/consolidado", response_model=list[FrequenciaConsolidada], summary="Consolidar frequência da turma", description="Retorna presenças, faltas e percentual por aluno matriculado.", responses={200: {"description": "Consolidado gerado."}, 401: {"description": "Token inválido ou ausente."}, 404: {"description": "Turma não encontrada."}})
async def consolidar_turma(turma_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[FrequenciaConsolidada]:
    await get_owned(db, Turma, turma_id, usuario, "Turma não encontrada.")
    rows = (
        await db.execute(
            select(Aluno.id, Aluno.nome, func.count(Frequencia.id), func.count(Frequencia.id).filter(Frequencia.presente.is_(True)))
            .join(Matricula, Matricula.aluno_id == Aluno.id)
            .outerjoin(Frequencia, (Frequencia.aluno_id == Aluno.id) & (Frequencia.turma_id == turma_id) & (Frequencia.rede_id == usuario.rede_id))
            .where(Matricula.turma_id == turma_id, Matricula.status == "ATIVA", Matricula.rede_id == usuario.rede_id)
            .group_by(Aluno.id, Aluno.nome)
            .order_by(Aluno.nome)
        )
    ).all()
    result = []
    for aluno_id, nome, aulas, presencas in rows:
        nivel = calcular_nivel_alerta(presencas, aulas)
        result.append(FrequenciaConsolidada(aluno_id=aluno_id, nome=nome, aulas=aulas, presencas=presencas, faltas=aulas - presencas, percentual=nivel.percentual, nivel_alerta=nivel.nivel))
    return result


@router.get("/busca-ativa", response_model=list[AlertaRead], summary="Listar busca ativa", description="Lista alertas de frequência não resolvidos da rede autenticada.", responses={200: {"description": "Alertas listados."}, 401: {"description": "Token inválido ou ausente."}})
async def listar_busca_ativa(usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limite: int = Query(100, ge=1, le=500)) -> list[AlertaFrequencia]:
    return (await db.execute(select(AlertaFrequencia).where(AlertaFrequencia.resolvido.is_(False), AlertaFrequencia.rede_id == usuario.rede_id).order_by(AlertaFrequencia.percentual).limit(limite))).scalars().all()
