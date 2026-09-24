from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers import criar_aluno, criar_estrutura, headers

client = TestClient(app)


def _matricular(aluno_id: int, turma_id: int, ano_letivo_id: int) -> None:
    response = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno_id, "turma_id": turma_id, "ano_letivo_id": ano_letivo_id},
        headers=headers(client),
    )
    assert response.status_code == 201, response.text


def test_chamada_e_idempotente_e_consolidada() -> None:
    _, ano, turma = criar_estrutura(client)
    presentes = [criar_aluno(client) for _ in range(2)]
    ausente = criar_aluno(client)
    for aluno in [*presentes, ausente]:
        _matricular(aluno["id"], turma["id"], ano["id"])

    payload = {
        "turma_id": turma["id"],
        "data": date.today().isoformat(),
        "ordem": 1,
        "itens": [
            {"aluno_id": presentes[0]["id"], "presente": True},
            {"aluno_id": presentes[1]["id"], "presente": True},
            {"aluno_id": ausente["id"], "presente": False},
        ],
    }
    auth = headers(client)
    first = client.post("/api/v1/frequencia/chamada", json=payload, headers=auth)
    assert first.status_code == 200, first.text
    second = client.post("/api/v1/frequencia/chamada", json=payload, headers=auth)
    assert second.status_code == 200, second.text
    assert len(second.json()) == 3

    consolidated = client.get(f"/api/v1/frequencia/turma/{turma['id']}/consolidado", headers=auth)
    assert consolidated.status_code == 200, consolidated.text
    aluno_ausente = next(item for item in consolidated.json() if item["aluno_id"] == ausente["id"])
    assert aluno_ausente["aulas"] == 1
    assert aluno_ausente["faltas"] == 1
    assert aluno_ausente["percentual"] in {"0.00", 0, "0.0"}

    dia = client.get(
        f"/api/v1/frequencia/turma/{turma['id']}/chamada",
        params={"data": date.today().isoformat(), "ordem": 1},
        headers=auth,
    )
    assert dia.status_code == 200, dia.text
    item_ausente = next(item for item in dia.json() if item["aluno_id"] == ausente["id"])
    assert item_ausente["presente"] is False
    assert item_ausente["registrada"] is True
    item_presente = next(item for item in dia.json() if item["aluno_id"] == presentes[0]["id"])
    assert item_presente["presente"] is True
    assert item_presente["registrada"] is True


def test_busca_ativa_retorna_alerta() -> None:
    _, ano, turma = criar_estrutura(client)
    aluno = criar_aluno(client)
    _matricular(aluno["id"], turma["id"], ano["id"])
    auth = headers(client)
    chamada = client.post(
        "/api/v1/frequencia/chamada",
        json={
            "turma_id": turma["id"],
            "data": date.today().isoformat(),
            "ordem": 1,
            "itens": [{"aluno_id": aluno["id"], "presente": False}],
        },
        headers=auth,
    )
    assert chamada.status_code == 200, chamada.text

    response = client.get("/api/v1/frequencia/busca-ativa", headers=auth)
    assert response.status_code == 200, response.text
    assert any(item["aluno_id"] == aluno["id"] and item["nivel"] == "LIMITE_LEGAL_30" for item in response.json())
