from __future__ import annotations

import asyncio
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import decode_access_token, hash_password
from app.db.session import engine
from app.main import app
from tests.helpers import criar_escola, headers

client = TestClient(app)


def test_login_e_me() -> None:
    login = client.post("/api/v1/auth/login", json={"email": "gestor@sga.local", "senha": "Gestor@123"})
    assert login.status_code == 200, login.text
    body = login.json()
    assert body["token_type"] == "bearer"
    claims = decode_access_token(body["access_token"])
    assert claims["perfil"] == "gestor"
    assert int(claims["rede_id"]) == 1

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "gestor@sga.local"


def test_login_rejeita_senha_errada() -> None:
    response = client.post("/api/v1/auth/login", json={"email": "gestor@sga.local", "senha": "errada123"})
    assert response.status_code == 401


def test_rota_protegida_exige_token() -> None:
    response = client.get("/api/v1/escolas")
    assert response.status_code == 401


def test_professor_nao_cadastra_escola() -> None:
    response = client.post(
        "/api/v1/escolas",
        json={"nome": "Escola do Professor", "ativo": True},
        headers=headers(client, email="professor@sga.local", senha="Professor@123"),
    )
    assert response.status_code == 403


def test_refresh_renova_token() -> None:
    auth = headers(client)
    response = client.post("/api/v1/auth/refresh", headers=auth)
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_isolamento_entre_duas_redes() -> None:
    escola = criar_escola(client, nome=f"Escola Rede Um {uuid4().hex[:6]}")
    email = f"gestor-{uuid4().hex[:8]}@sga.local"
    senha = "OutraRede@123"

    async def criar_outra_rede() -> None:
        hashed = hash_password(senha)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT setval(pg_get_serial_sequence('sga.rede', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sga.rede))"))
            rede_id = await conn.scalar(text("INSERT INTO sga.rede (nome, ativo) VALUES (:nome, TRUE) RETURNING id"), {"nome": f"Rede {uuid4().hex[:8]}"})
            await conn.execute(
                text("INSERT INTO sga.usuario (rede_id, escola_id, nome, email, senha_hash, perfil) VALUES (:rede_id, NULL, :nome, :email, :senha_hash, 'gestor')"),
                {"rede_id": rede_id, "nome": "Gestor Isolado", "email": email, "senha_hash": hashed},
            )

    asyncio.run(criar_outra_rede())
    outro = TestClient(app)
    login = outro.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    listagem = outro.get("/api/v1/escolas", params={"limit": 200}, headers=auth)
    assert listagem.status_code == 200
    assert all(item["id"] != escola["id"] for item in listagem.json())

    detalhe = outro.get(f"/api/v1/escolas/{escola['id']}", headers=auth)
    assert detalhe.status_code == 404
