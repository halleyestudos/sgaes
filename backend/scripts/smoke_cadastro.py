from __future__ import annotations

import uuid

import httpx

base = "http://127.0.0.1:8000"
suffix = uuid.uuid4().hex[:8]


def main() -> None:
    with httpx.Client(base_url=base, timeout=10) as client:
        health = client.get("/health")
        assert health.status_code == 200, health.text
        assert health.json()["status"] == "ok"

        escola = client.post("/api/v1/escolas", json={"nome": f"Escola Live {suffix}", "rede_id": 1, "ativo": True})
        print("escola", escola.status_code, escola.json())
        assert escola.status_code == 201

        ano = client.post("/api/v1/anos-letivos", json={"nome": f"L{suffix[:7]}", "rede_id": 1, "ativo": True})
        print("ano", ano.status_code, ano.json())
        assert ano.status_code == 201

        turma = client.post(
            "/api/v1/turmas",
            json={
                "nome": f"Turma Live {suffix}",
                "serie": "1° Ano",
                "turno": "manhã",
                "ativa": True,
                "rede_id": 1,
                "escola_id": escola.json()["id"],
                "ano_letivo_id": ano.json()["id"],
            },
        )
        print("turma", turma.status_code, turma.json())
        assert turma.status_code == 201

        aluno = client.post("/api/v1/alunos", json={"nome": f"Aluno Live {suffix}", "rede_id": 1, "ativo": True})
        print("aluno", aluno.status_code, aluno.json())
        assert aluno.status_code == 201

        matricula = client.post(
            "/api/v1/matriculas",
            json={
                "aluno_id": aluno.json()["id"],
                "turma_id": turma.json()["id"],
                "ano_letivo_id": ano.json()["id"],
                "rede_id": 1,
            },
        )
        print("matricula", matricula.status_code, matricula.json())
        assert matricula.status_code == 201

        duplicada = client.post(
            "/api/v1/matriculas",
            json={
                "aluno_id": aluno.json()["id"],
                "turma_id": turma.json()["id"],
                "ano_letivo_id": ano.json()["id"],
                "rede_id": 1,
            },
        )
        print("duplicada", duplicada.status_code, duplicada.json())
        assert duplicada.status_code == 409

        alunos_turma = client.get(f"/api/v1/matriculas/turma/{turma.json()['id']}/alunos")
        print("alunos_turma", alunos_turma.status_code, alunos_turma.json())
        assert any(item["aluno_id"] == aluno.json()["id"] for item in alunos_turma.json())

        consolidado = client.get(f"/api/v1/frequencia/turma/{turma.json()['id']}/consolidado")
        print("consolidado", consolidado.status_code, consolidado.json())
        assert consolidado.status_code == 200
        assert any(item["aluno_id"] == aluno.json()["id"] for item in consolidado.json())

        print("OK cadastro live")


if __name__ == "__main__":
    main()
