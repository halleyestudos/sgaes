from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.db.session import engine

MAX_ALUNOS = 30


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("SET search_path TO sga, public"))

        escola_id = await conn.scalar(text("SELECT id FROM sga.escola ORDER BY id LIMIT 1"))
        ano_id = await conn.scalar(text("SELECT id FROM sga.ano_letivo ORDER BY id LIMIT 1"))
        if escola_id is None or ano_id is None:
            raise RuntimeError("É preciso ter pelo menos uma escola e um ano letivo.")

        # Remove frequência e matrículas; depois todas as turmas.
        await conn.execute(text("DELETE FROM sga.frequencia"))
        await conn.execute(text("DELETE FROM sga.alerta_frequencia"))
        await conn.execute(text("DELETE FROM sga.matricula"))
        await conn.execute(text("DELETE FROM sga.turma"))

        # Recria 10 turmas com nomes claros.
        nomes = [
            ("1º Ano A", "1° Ano", "manhã"),
            ("1º Ano B", "1° Ano", "tarde"),
            ("2º Ano A", "2° Ano", "manhã"),
            ("2º Ano B", "2° Ano", "tarde"),
            ("3º Ano A", "3° Ano", "manhã"),
            ("3º Ano B", "3° Ano", "tarde"),
            ("4º Ano A", "4° Ano", "manhã"),
            ("4º Ano B", "4° Ano", "tarde"),
            ("5º Ano A", "5° Ano", "manhã"),
            ("5º Ano B", "5° Ano", "tarde"),
        ]
        turma_ids: list[int] = []
        for nome, serie, turno in nomes:
            turma_id = await conn.scalar(
                text(
                    """
                    INSERT INTO sga.turma (rede_id, escola_id, ano_letivo_id, nome, serie, turno, ativa)
                    VALUES (1, :escola_id, :ano_id, :nome, :serie, :turno, TRUE)
                    RETURNING id
                    """
                ),
                {"escola_id": escola_id, "ano_id": ano_id, "nome": nome, "serie": serie, "turno": turno},
            )
            turma_ids.append(int(turma_id))

        # Mantém no máximo 90 alunos ativos para encher 3 turmas com 30.
        alunos = (
            await conn.execute(text("SELECT id FROM sga.aluno WHERE ativo IS TRUE ORDER BY id"))
        ).scalars().all()
        alunos = list(alunos)[:90]

        # Remove alunos excedentes sem vínculo.
        extras = (
            await conn.execute(
                text("SELECT id FROM sga.aluno WHERE id <> ALL(:keep)"),
                {"keep": alunos or [0]},
            )
        ).scalars().all()
        if extras:
            await conn.execute(text("DELETE FROM sga.aluno WHERE id = ANY(:ids)"), {"ids": list(extras)})

        # Matricula: turmas 1,2,3 com 30; demais vazias.
        for index, aluno_id in enumerate(alunos):
            turma_id = turma_ids[index // MAX_ALUNOS]
            await conn.execute(
                text(
                    """
                    INSERT INTO sga.matricula (rede_id, aluno_id, turma_id, ano_letivo_id, status, data_matricula)
                    VALUES (1, :aluno_id, :turma_id, :ano_id, 'ATIVA', CURRENT_DATE)
                    """
                ),
                {"aluno_id": aluno_id, "turma_id": turma_id, "ano_id": ano_id},
            )

        await conn.execute(text("SELECT setval(pg_get_serial_sequence('sga.turma', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sga.turma))"))

        print("--- resultado ---")
        print("turmas", (await conn.execute(text("SELECT COUNT(*) FROM sga.turma"))).scalar())
        print("alunos", (await conn.execute(text("SELECT COUNT(*) FROM sga.aluno"))).scalar())
        rows = (
            await conn.execute(
                text(
                    """
                    SELECT t.id, t.nome, t.serie, t.turno, COUNT(m.id) AS ativos
                    FROM sga.turma t
                    LEFT JOIN sga.matricula m ON m.turma_id = t.id AND m.status = 'ATIVA'
                    GROUP BY t.id, t.nome, t.serie, t.turno
                    ORDER BY t.id
                    """
                )
            )
        ).all()
        for row in rows:
            print(tuple(row))


if __name__ == "__main__":
    asyncio.run(main())
