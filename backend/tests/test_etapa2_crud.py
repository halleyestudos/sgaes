from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from tests.helpers import criar_aluno, criar_ano_letivo, criar_escola, criar_estrutura, headers, sufixo

client = TestClient(app)


def test_criar_e_listar_escola() -> None:
    nome = f"Escola {sufixo()}"
    data = criar_escola(client, nome=nome)
    assert data["nome"] == nome
    assert data["rede_id"] == 1
    assert data["ativo"] is True

    listagem = client.get("/api/v1/escolas", params={"limit": 200}, headers=headers(client))
    assert listagem.status_code == 200
    assert any(item["id"] == data["id"] for item in listagem.json())


def test_atualizar_e_inativar_escola() -> None:
    escola = criar_escola(client)
    response = client.put(f"/api/v1/escolas/{escola['id']}", json={"nome": "Escola Atualizada", "ativo": False}, headers=headers(client))
    assert response.status_code == 200, response.text
    assert response.json()["nome"] == "Escola Atualizada"
    assert response.json()["ativo"] is False


def test_criar_ano_letivo_unico_por_rede() -> None:
    nome = f"A{sufixo()[:7]}"
    primeiro = criar_ano_letivo(client, nome=nome)
    assert primeiro["nome"] == nome

    duplicado = client.post("/api/v1/anos-letivos", json={"nome": nome, "ativo": True}, headers=headers(client))
    assert duplicado.status_code == 409
    assert "ano letivo" in duplicado.json()["detail"].lower()


def test_criar_turma_vinculada_a_escola_e_ano() -> None:
    escola, ano, turma = criar_estrutura(client)
    assert turma["escola_id"] == escola["id"]
    assert turma["ano_letivo_id"] == ano["id"]
    assert turma["ativa"] is True


def test_criar_turma_com_escola_inexistente_retorna_nao_encontrada() -> None:
    ano = criar_ano_letivo(client)
    response = client.post(
        "/api/v1/turmas",
        json={
            "nome": f"Turma {sufixo()}",
            "serie": "2° Ano",
            "turno": "tarde",
            "ativa": True,
            "escola_id": 9_999_999,
            "ano_letivo_id": ano["id"],
        },
        headers=headers(client),
    )
    assert response.status_code == 404


def test_cadastrar_aluno_somente_com_nome() -> None:
    aluno = criar_aluno(client, nome="Maria Oliveira")
    assert aluno["nome"] == "Maria Oliveira"
    assert aluno["ativo"] is True
    assert aluno["id"] > 0


def test_rejeitar_aluno_com_nome_curto() -> None:
    response = client.post("/api/v1/alunos", json={"nome": "A"}, headers=headers(client))
    assert response.status_code == 422


def test_busca_por_nome_aluno() -> None:
    nome = f"Ana Beatriz {sufixo()}"
    criado = criar_aluno(client, nome=nome)
    busca = client.get("/api/v1/alunos/buscar", params={"nome": "Ana Beatriz"}, headers=headers(client))
    assert busca.status_code == 200
    assert any(item["id"] == criado["id"] for item in busca.json())


def test_inativar_aluno_preserva_registro() -> None:
    aluno = criar_aluno(client)
    response = client.put(f"/api/v1/alunos/{aluno['id']}", json={"ativo": False}, headers=headers(client))
    assert response.status_code == 200
    assert response.json()["ativo"] is False
    obtido = client.get(f"/api/v1/alunos/{aluno['id']}", headers=headers(client))
    assert obtido.status_code == 200
    assert obtido.json()["id"] == aluno["id"]
