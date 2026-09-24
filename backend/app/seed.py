from __future__ import annotations

import asyncio
import logging
from datetime import date

from sqlalchemy import text

from app.core.config import get_settings
from app.core.security import hash_password
from app.core.logging import configure_logging
from app.db.session import engine

logger = logging.getLogger(__name__)


async def ensure_schema() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sga"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))


async def _scalar(conn, sql: str, params: dict | None = None):
    return await conn.scalar(text(sql), params or {})


async def _table_exists(conn, table_name: str) -> bool:
    return bool(await _scalar(conn, "SELECT to_regclass(:name)", {"name": f"sga.{table_name}"}))


async def seed() -> None:
    settings = get_settings()
    async with engine.begin() as conn:
        await conn.execute(text("SET search_path TO sga, public"))

        if not await _table_exists(conn, "aluno"):
            raise RuntimeError("Schema incompleto. Execute `python -m alembic upgrade head` antes do seed.")

        await conn.execute(
            text("INSERT INTO sga.rede (id, nome, ativo) VALUES (:id, :nome, :ativo) ON CONFLICT (id) DO NOTHING"),
            {"id": settings.default_rede_id, "nome": "Rede Municipal de Teste", "ativo": True},
        )
        await conn.execute(text("SELECT setval(pg_get_serial_sequence('sga.rede', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sga.rede))"))

        escola_id = await _scalar(conn, "SELECT id FROM sga.escola WHERE rede_id = :rede_id ORDER BY id LIMIT 1", {"rede_id": settings.default_rede_id})
        if escola_id is None:
            escola_id = await _scalar(
                conn,
                """
                INSERT INTO sga.escola (
                    rede_id, nome, codigo_inep, dependencia_administrativa, bairro, cidade, uf,
                    latitude, longitude, ativo
                ) VALUES (
                    :rede_id, :nome, :codigo_inep, :dependencia_administrativa, :bairro, :cidade, :uf,
                    :latitude, :longitude, :ativo
                ) RETURNING id
                """,
                {
                    "rede_id": settings.default_rede_id,
                    "nome": "Escola Municipal Modelo",
                    "codigo_inep": "53000000",
                    "dependencia_administrativa": "municipal",
                    "bairro": "Asa Sul",
                    "cidade": "Brasília",
                    "uf": "DF",
                    "latitude": -15.7942,
                    "longitude": -47.8822,
                    "ativo": True,
                },
            )
        else:
            await conn.execute(
                text(
                    """
                    UPDATE sga.escola
                    SET dependencia_administrativa = COALESCE(dependencia_administrativa, 'municipal'),
                        bairro = COALESCE(bairro, 'Asa Sul'),
                        cidade = COALESCE(cidade, 'Brasília'),
                        uf = COALESCE(uf, 'DF'),
                        latitude = COALESCE(latitude, -15.7942),
                        longitude = COALESCE(longitude, -47.8822)
                    WHERE id = :id
                    """
                ),
                {"id": escola_id},
            )

        ano_letivo_id = await _scalar(conn, "SELECT id FROM sga.ano_letivo WHERE rede_id = :rede_id ORDER BY id LIMIT 1", {"rede_id": settings.default_rede_id})
        if ano_letivo_id is None:
            ano_letivo_id = await _scalar(
                conn,
                "INSERT INTO sga.ano_letivo (rede_id, nome, ativo) VALUES (:rede_id, :nome, :ativo) RETURNING id",
                {"rede_id": settings.default_rede_id, "nome": "2026", "ativo": True},
            )

        aluno_count = await _scalar(conn, "SELECT COUNT(*) FROM sga.aluno WHERE rede_id = :rede_id", {"rede_id": settings.default_rede_id})
        if not aluno_count:
            for idx in range(1, 61):
                await conn.execute(
                    text("INSERT INTO sga.aluno (rede_id, nome, nome_social, data_nascimento, sexo, ativo) VALUES (:rede_id, :nome, :nome_social, :data_nascimento, :sexo, :ativo)"),
                    {
                        "rede_id": settings.default_rede_id,
                        "nome": f"Aluno {idx:02d}",
                        "nome_social": None,
                        "data_nascimento": date(2016, (idx % 12) + 1, min((idx % 28) + 1, 28)),
                        "sexo": "F" if idx % 2 == 0 else "M",
                        "ativo": True,
                    },
                )

        turma_ids: list[int] = []
        for idx in range(1, 4):
            turma_name = f"Turma {idx}"
            turma_id = await _scalar(
                conn,
                "SELECT id FROM sga.turma WHERE rede_id = :rede_id AND escola_id = :escola_id AND ano_letivo_id = :ano_letivo_id AND nome = :nome",
                {
                    "rede_id": settings.default_rede_id,
                    "escola_id": escola_id,
                    "ano_letivo_id": ano_letivo_id,
                    "nome": turma_name,
                },
            )
            if turma_id is None:
                turma_id = await _scalar(
                    conn,
                    "INSERT INTO sga.turma (rede_id, escola_id, ano_letivo_id, nome, serie, turno, ativa) VALUES (:rede_id, :escola_id, :ano_letivo_id, :nome, :serie, :turno, :ativa) RETURNING id",
                    {
                        "rede_id": settings.default_rede_id,
                        "escola_id": escola_id,
                        "ano_letivo_id": ano_letivo_id,
                        "nome": turma_name,
                        "serie": f"{idx}° Ano",
                        "turno": "manhã" if idx % 2 == 1 else "tarde",
                        "ativa": True,
                    },
                )
            turma_ids.append(int(turma_id))

        if await _table_exists(conn, "matricula") and turma_ids:
            alunos = (await conn.execute(text("SELECT id FROM sga.aluno WHERE rede_id = :rede_id AND ativo IS TRUE ORDER BY id"), {"rede_id": settings.default_rede_id})).all()
            for index, (aluno_id,) in enumerate(alunos):
                turma_id = turma_ids[index % len(turma_ids)]
                await conn.execute(
                    text(
                        """
                        INSERT INTO sga.matricula (rede_id, aluno_id, turma_id, ano_letivo_id, status, data_matricula)
                        SELECT :rede_id, :aluno_id, :turma_id, :ano_letivo_id, 'ATIVA', CURRENT_DATE
                        WHERE NOT EXISTS (
                            SELECT 1 FROM sga.matricula
                            WHERE aluno_id = :aluno_id AND ano_letivo_id = :ano_letivo_id AND status = 'ATIVA'
                        )
                        """
                    ),
                    {
                        "rede_id": settings.default_rede_id,
                        "aluno_id": aluno_id,
                        "turma_id": turma_id,
                        "ano_letivo_id": ano_letivo_id,
                    },
                )

        if await _table_exists(conn, "usuario"):
            demo_users = [
                {"nome": "Gestor Municipal", "email": "gestor@sga.local", "senha": "Gestor@123", "perfil": "gestor", "escola_id": None},
                {"nome": "Professor Responsável", "email": "professor@sga.local", "senha": "Professor@123", "perfil": "professor", "escola_id": escola_id},
                {"nome": "Secretaria Escolar", "email": "secretaria@sga.local", "senha": "Secretaria@123", "perfil": "secretaria", "escola_id": escola_id},
            ]
            for user in demo_users:
                existing_id = await _scalar(conn, "SELECT id FROM sga.usuario WHERE email = :email", {"email": user["email"]})
                hashed = hash_password(user["senha"])
                if existing_id:
                    await conn.execute(
                        text("UPDATE sga.usuario SET senha_hash = :senha_hash, nome = :nome, perfil = :perfil, escola_id = :escola_id, rede_id = :rede_id WHERE id = :id"),
                        {
                            "senha_hash": hashed,
                            "nome": user["nome"],
                            "perfil": user["perfil"],
                            "escola_id": user["escola_id"],
                            "rede_id": settings.default_rede_id,
                            "id": existing_id,
                        },
                    )
                else:
                    await conn.execute(
                        text("INSERT INTO sga.usuario (rede_id, escola_id, nome, email, senha_hash, perfil) VALUES (:rede_id, :escola_id, :nome, :email, :senha_hash, :perfil)"),
                        {
                            "rede_id": settings.default_rede_id,
                            "escola_id": user["escola_id"],
                            "nome": user["nome"],
                            "email": user["email"],
                            "senha_hash": hashed,
                            "perfil": user["perfil"],
                        },
                    )

    logger.info("seed_completed", extra={"rede_id": settings.default_rede_id})


async def main() -> None:
    configure_logging()
    logger.info("seed_starting")
    await ensure_schema()
    await seed()
    logger.info("seed_finished")


if __name__ == "__main__":
    asyncio.run(main())
