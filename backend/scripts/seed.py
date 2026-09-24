from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


async def seed() -> None:
    settings = get_settings()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sga"))
        await conn.execute(text("SET search_path TO sga, public"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.rede (id SERIAL PRIMARY KEY, nome VARCHAR(255) NOT NULL, ativo BOOLEAN DEFAULT TRUE)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.escola (id SERIAL PRIMARY KEY, rede_id INTEGER NOT NULL, nome VARCHAR(255) NOT NULL, codigo_inep VARCHAR(20), ativo BOOLEAN DEFAULT TRUE)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.ano_letivo (id SERIAL PRIMARY KEY, rede_id INTEGER NOT NULL, nome VARCHAR(20) NOT NULL, ativo BOOLEAN DEFAULT TRUE)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.turma (id SERIAL PRIMARY KEY, rede_id INTEGER NOT NULL, escola_id INTEGER NOT NULL, ano_letivo_id INTEGER NOT NULL, nome VARCHAR(100) NOT NULL, serie VARCHAR(20), turno VARCHAR(20))"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.aluno (id SERIAL PRIMARY KEY, rede_id INTEGER NOT NULL, nome VARCHAR(255) NOT NULL, data_nascimento DATE, sexo VARCHAR(20), ativo BOOLEAN DEFAULT TRUE)"))
        await conn.execute(text("CREATE TABLE IF NOT EXISTS sga.usuario (id SERIAL PRIMARY KEY, rede_id INTEGER NOT NULL, escola_id INTEGER, nome VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, senha_hash VARCHAR(255) NOT NULL, perfil VARCHAR(50) NOT NULL)"))

        await conn.execute(text("INSERT INTO sga.rede (id, nome, ativo) VALUES (:id, :nome, :ativo) ON CONFLICT (id) DO NOTHING"), {"id": settings.default_rede_id, "nome": "Rede Municipal Teste", "ativo": True})
        await conn.execute(text("INSERT INTO sga.escola (rede_id, nome, codigo_inep, ativo) VALUES (:rede_id, :nome, :codigo_inep, :ativo) ON CONFLICT DO NOTHING"), {"rede_id": settings.default_rede_id, "nome": "Escola Modelo", "codigo_inep": "53000000", "ativo": True})
        await conn.execute(text("INSERT INTO sga.ano_letivo (rede_id, nome, ativo) VALUES (:rede_id, :nome, :ativo) ON CONFLICT DO NOTHING"), {"rede_id": settings.default_rede_id, "nome": "2026", "ativo": True})

        await conn.execute(text("INSERT INTO sga.usuario (rede_id, escola_id, nome, email, senha_hash, perfil) VALUES (:rede_id, :escola_id, :nome, :email, :senha_hash, :perfil) ON CONFLICT (email) DO NOTHING"), {
            "rede_id": settings.default_rede_id,
            "escola_id": 1,
            "nome": "Gestor",
            "email": "gestor@sga.local",
            "senha_hash": "$argon2id$v=19$m=65536,t=3,p=4$QjK+S5NdWk0Qh7o0rFZ3BQ$CzL3F0D1JYb8VbXyq3hM8QaP9vQ0k8i0x8xT5gPqC8",
            "perfil": "gestor",
        })
        await conn.execute(text("INSERT INTO sga.usuario (rede_id, escola_id, nome, email, senha_hash, perfil) VALUES (:rede_id, :escola_id, :nome, :email, :senha_hash, :perfil) ON CONFLICT (email) DO NOTHING"), {
            "rede_id": settings.default_rede_id,
            "escola_id": 1,
            "nome": "Professor",
            "email": "professor@sga.local",
            "senha_hash": "$argon2id$v=19$m=65536,t=3,p=4$QjK+S5NdWk0Qh7o0rFZ3BQ$CzL3F0D1JYb8VbXyq3hM8QaP9vQ0k8i0x8xT5gPqC8",
            "perfil": "professor",
        })

    print("Seed finalizado.")


if __name__ == "__main__":
    asyncio.run(seed())
