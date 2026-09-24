from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

_tokens: dict[str, str] = {}


def sufixo() -> str:
    return uuid4().hex[:8]


def headers(client: TestClient, email: str = "gestor@sga.local", senha: str = "Gestor@123") -> dict[str, str]:
    key = f"{id(client)}:{email}"
    if key not in _tokens:
        response = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
        assert response.status_code == 200, response.text
        _tokens[key] = response.json()["access_token"]
    return {"Authorization": f"Bearer {_tokens[key]}"}


def criar_escola(client: TestClient, *, nome: str | None = None) -> dict:
    payload = {"nome": nome or f"Escola {sufixo()}", "codigo_inep": None, "ativo": True}
    response = client.post("/api/v1/escolas", json=payload, headers=headers(client))
    assert response.status_code == 201, response.text
    return response.json()


def criar_ano_letivo(client: TestClient, *, nome: str | None = None) -> dict:
    payload = {"nome": nome or f"A{sufixo()[:7]}", "ativo": True}
    response = client.post("/api/v1/anos-letivos", json=payload, headers=headers(client))
    assert response.status_code == 201, response.text
    return response.json()


def criar_turma(client: TestClient, *, escola_id: int, ano_letivo_id: int, nome: str | None = None) -> dict:
    payload = {
        "nome": nome or f"Turma {sufixo()}",
        "serie": "1° Ano",
        "turno": "manhã",
        "ativa": True,
        "escola_id": escola_id,
        "ano_letivo_id": ano_letivo_id,
    }
    response = client.post("/api/v1/turmas", json=payload, headers=headers(client))
    assert response.status_code == 201, response.text
    return response.json()


def criar_aluno(client: TestClient, *, nome: str | None = None) -> dict:
    payload = {"nome": nome or f"Aluno {sufixo()}", "ativo": True}
    response = client.post("/api/v1/alunos", json=payload, headers=headers(client))
    assert response.status_code == 201, response.text
    return response.json()


def criar_estrutura(client: TestClient) -> tuple[dict, dict, dict]:
    escola = criar_escola(client)
    ano = criar_ano_letivo(client)
    turma = criar_turma(client, escola_id=escola["id"], ano_letivo_id=ano["id"])
    return escola, ano, turma
