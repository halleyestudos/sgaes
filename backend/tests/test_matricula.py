from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers import criar_aluno, criar_estrutura, criar_turma, headers, sufixo

client = TestClient(app)


def test_fluxo_matricula_transferencia_e_encerramento() -> None:
    _, ano, turma_origem = criar_estrutura(client)
    turma_destino = criar_turma(client, escola_id=turma_origem["escola_id"], ano_letivo_id=ano["id"], nome=f"Destino {sufixo()}")
    aluno = criar_aluno(client, nome=f"Aluno Matrícula {sufixo()}")
    auth = headers(client)

    matricula = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno["id"], "turma_id": turma_origem["id"], "ano_letivo_id": ano["id"]},
        headers=auth,
    )
    assert matricula.status_code == 201, matricula.text
    matricula_id = matricula.json()["id"]

    alunos = client.get(f"/api/v1/matriculas/turma/{turma_origem['id']}/alunos", headers=auth)
    assert alunos.status_code == 200
    assert any(item["aluno_id"] == aluno["id"] for item in alunos.json())

    transferencia = client.put(
        f"/api/v1/matriculas/{matricula_id}/transferir",
        json={"nova_turma_id": turma_destino["id"], "motivo": "Reorganização pedagógica"},
        headers=auth,
    )
    assert transferencia.status_code == 200, transferencia.text
    nova_matricula_id = transferencia.json()["id"]
    assert transferencia.json()["turma_id"] == turma_destino["id"]

    encerramento = client.put(
        f"/api/v1/matriculas/{nova_matricula_id}/encerrar",
        json={"motivo": "Transferência para outra rede"},
        headers=auth,
    )
    assert encerramento.status_code == 200, encerramento.text
    assert encerramento.json()["status"] == "ENCERRADA"

    reabertura = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno["id"], "turma_id": turma_origem["id"], "ano_letivo_id": ano["id"]},
        headers=auth,
    )
    assert reabertura.status_code == 201, reabertura.text


def test_recusar_matricula_duplicada_no_mesmo_ano() -> None:
    _, ano, turma = criar_estrutura(client)
    aluno = criar_aluno(client)
    auth = headers(client)
    primeira = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno["id"], "turma_id": turma["id"], "ano_letivo_id": ano["id"]},
        headers=auth,
    )
    assert primeira.status_code == 201, primeira.text

    duplicada = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno["id"], "turma_id": turma["id"], "ano_letivo_id": ano["id"]},
        headers=auth,
    )
    assert duplicada.status_code == 409
    assert "matrícula ativa" in duplicada.json()["detail"].lower()


def test_recusar_turma_de_outro_ano_letivo() -> None:
    escola, ano, turma = criar_estrutura(client)
    auth = headers(client)
    outro_ano = client.post("/api/v1/anos-letivos", json={"nome": f"B{sufixo()[:7]}", "ativo": True}, headers=auth)
    assert outro_ano.status_code == 201, outro_ano.text
    aluno = criar_aluno(client)
    response = client.post(
        "/api/v1/matriculas",
        json={"aluno_id": aluno["id"], "turma_id": turma["id"], "ano_letivo_id": outro_ano.json()["id"]},
        headers=auth,
    )
    assert response.status_code == 400
    assert "ano letivo" in response.json()["detail"].lower()
    assert escola["id"] == turma["escola_id"]
