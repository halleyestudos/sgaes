from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.security import hash_password
from app.db.session import engine

DEMO_USERS = (
    {"nome": "Gestor Municipal", "email": "gestor@sga.local", "senha": "Gestor@123", "perfil": "gestor", "escola_id": None},
    {"nome": "Professor Responsável", "email": "professor@sga.local", "senha": "Professor@123", "perfil": "professor", "escola_id": None},
    {"nome": "Secretaria Escolar", "email": "secretaria@sga.local", "senha": "Secretaria@123", "perfil": "secretaria", "escola_id": None},
)


async def _ensure_demo_users() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("INSERT INTO sga.rede (id, nome, ativo) VALUES (1, 'Rede Municipal de Teste', TRUE) ON CONFLICT (id) DO NOTHING"))
        for user in DEMO_USERS:
            existing_id = await conn.scalar(text("SELECT id FROM sga.usuario WHERE email = :email"), {"email": user["email"]})
            hashed = hash_password(user["senha"])
            if existing_id:
                await conn.execute(
                    text("UPDATE sga.usuario SET senha_hash = :senha_hash, perfil = :perfil, nome = :nome, rede_id = 1 WHERE id = :id"),
                    {"senha_hash": hashed, "perfil": user["perfil"], "nome": user["nome"], "id": existing_id},
                )
            else:
                await conn.execute(
                    text("INSERT INTO sga.usuario (rede_id, escola_id, nome, email, senha_hash, perfil) VALUES (1, :escola_id, :nome, :email, :senha_hash, :perfil)"),
                    {
                        "escola_id": user["escola_id"],
                        "nome": user["nome"],
                        "email": user["email"],
                        "senha_hash": hashed,
                        "perfil": user["perfil"],
                    },
                )


def pytest_sessionstart(session) -> None:
    asyncio.run(_ensure_demo_users())
