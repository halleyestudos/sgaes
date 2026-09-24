from __future__ import annotations

"""Carga demonstrativa: escolas em Serra-ES e Vitória-ES + alunos próximos.

Uso:
  cd backend
  .\\.venv\\Scripts\\python.exe scripts\\carga_geo_es.py

No container Dokploy (Open Terminal do serviço api):
  python scripts/carga_geo_es.py
"""

import asyncio
import os
from datetime import date, timedelta
from decimal import Decimal
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.services.geo_service import calcular_deslocamento


ESCOLAS = [
    {
        "nome": "EMEF Centro de Vitória",
        "codigo_inep": "32010001",
        "bairro": "Centro",
        "cidade": "Vitória",
        "uf": "ES",
        "endereco": "Av. Jerônimo Monteiro, 100",
        "latitude": -20.3194,
        "longitude": -40.3375,
        "turma": "1º Ano Vitória",
    },
    {
        "nome": "EMEF Laranjeiras Serra",
        "codigo_inep": "32020002",
        "bairro": "Laranjeiras",
        "cidade": "Serra",
        "uf": "ES",
        "endereco": "Av. Talma Rodrigues Ribeiro, 500",
        "latitude": -20.2095,
        "longitude": -40.2610,
        "turma": "1º Ano Serra",
    },
]

# 3 alunos perto de Vitória + 2 perto de Serra
ALUNOS = [
    {
        "nome": "Ana Vitória Costa",
        "bairro": "Praia do Canto",
        "cidade": "Vitória",
        "endereco": "Rua Joaquim Lírio, 120",
        "latitude": -20.3025,
        "longitude": -40.2920,
        "modal": "onibus_escolar",
        "escola_idx": 0,
    },
    {
        "nome": "Bruno Capixaba Silva",
        "bairro": "Jardim da Penha",
        "cidade": "Vitória",
        "endereco": "Av. Fernando Ferrari, 890",
        "latitude": -20.2780,
        "longitude": -40.3005,
        "modal": "transporte_publico",
        "escola_idx": 0,
    },
    {
        "nome": "Carla Enseada Souza",
        "bairro": "Enseada do Suá",
        "cidade": "Vitória",
        "endereco": "Rua Aleixo Neto, 45",
        "latitude": -20.3108,
        "longitude": -40.2955,
        "modal": "a_pe",
        "escola_idx": 0,
    },
    {
        "nome": "Diego Serra Oliveira",
        "bairro": "Laranjeiras",
        "cidade": "Serra",
        "endereco": "Rua das Acácias, 210",
        "latitude": -20.2150,
        "longitude": -40.2550,
        "modal": "a_pe",
        "escola_idx": 1,
    },
    {
        "nome": "Elena Jacaraípe Lima",
        "bairro": "Jacaraípe",
        "cidade": "Serra",
        "endereco": "Av. Bahia, 1500",
        "latitude": -20.1420,
        "longitude": -40.2100,
        "modal": "onibus_escolar",
        "escola_idx": 1,
    },
]


async def _scalar(conn, sql: str, params: dict | None = None):
    return await conn.scalar(text(sql), params or {})


async def main() -> None:
    password = os.environ.get("POSTGRES_PASSWORD")
    if password:
        database_url = f"postgresql+asyncpg://postgres:{quote_plus(password)}@db:5432/sga"
    else:
        database_url = os.environ.get(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/sga",
        )
    engine = create_async_engine(database_url, pool_pre_ping=True)
    rede_id = int(os.environ.get("DEFAULT_REDE_ID", "1"))

    async with engine.begin() as conn:
        await conn.execute(text("SET search_path TO sga, public"))

        ano_id = await _scalar(
            conn,
            "SELECT id FROM sga.ano_letivo WHERE rede_id = :rede_id AND ativo IS TRUE ORDER BY id DESC LIMIT 1",
            {"rede_id": rede_id},
        )
        if ano_id is None:
            ano_id = await _scalar(
                conn,
                "INSERT INTO sga.ano_letivo (rede_id, nome, ativo) VALUES (:rede_id, '2026', true) RETURNING id",
                {"rede_id": rede_id},
            )

        escola_ids: list[int] = []
        turma_ids: list[int] = []
        for escola in ESCOLAS:
            existente = await _scalar(
                conn,
                "SELECT id FROM sga.escola WHERE rede_id = :rede_id AND codigo_inep = :codigo",
                {"rede_id": rede_id, "codigo": escola["codigo_inep"]},
            )
            if existente:
                escola_id = existente
                await conn.execute(
                    text(
                        """
                        UPDATE sga.escola SET
                          nome = :nome, dependencia_administrativa = 'municipal',
                          endereco = :endereco, bairro = :bairro, cidade = :cidade, uf = :uf,
                          latitude = :latitude, longitude = :longitude, ativo = true
                        WHERE id = :id
                        """
                    ),
                    {**escola, "id": escola_id},
                )
            else:
                escola_id = await _scalar(
                    conn,
                    """
                    INSERT INTO sga.escola (
                      rede_id, nome, codigo_inep, dependencia_administrativa,
                      endereco, bairro, cidade, uf, latitude, longitude, ativo
                    ) VALUES (
                      :rede_id, :nome, :codigo_inep, 'municipal',
                      :endereco, :bairro, :cidade, :uf, :latitude, :longitude, true
                    ) RETURNING id
                    """,
                    {"rede_id": rede_id, **escola},
                )
            escola_ids.append(int(escola_id))

            turma_id = await _scalar(
                conn,
                """
                SELECT id FROM sga.turma
                WHERE rede_id = :rede_id AND escola_id = :escola_id AND nome = :nome
                LIMIT 1
                """,
                {"rede_id": rede_id, "escola_id": escola_id, "nome": escola["turma"]},
            )
            if turma_id is None:
                turma_id = await _scalar(
                    conn,
                    """
                    INSERT INTO sga.turma (
                      rede_id, escola_id, ano_letivo_id, nome, serie, turno,
                      oferece_merenda, apoio_pedagogico, ativa
                    ) VALUES (
                      :rede_id, :escola_id, :ano_id, :nome, '1º Ano', 'manhã',
                      true, true, true
                    ) RETURNING id
                    """,
                    {
                        "rede_id": rede_id,
                        "escola_id": escola_id,
                        "ano_id": ano_id,
                        "nome": escola["turma"],
                    },
                )
            turma_ids.append(int(turma_id))

        print("--- escolas/turmas ---")
        for escola, eid, tid in zip(ESCOLAS, escola_ids, turma_ids):
            print(f"{escola['nome']} id={eid} turma_id={tid} ({escola['cidade']})")

        print("--- alunos + deslocamento ---")
        for idx, aluno in enumerate(ALUNOS, start=1):
            escola = ESCOLAS[aluno["escola_idx"]]
            escola_id = escola_ids[aluno["escola_idx"]]
            turma_id = turma_ids[aluno["escola_idx"]]

            aluno_id = await _scalar(
                conn,
                "SELECT id FROM sga.aluno WHERE rede_id = :rede_id AND nome = :nome LIMIT 1",
                {"rede_id": rede_id, "nome": aluno["nome"]},
            )
            params = {
                "rede_id": rede_id,
                "nome": aluno["nome"],
                "endereco": aluno["endereco"],
                "bairro": aluno["bairro"],
                "cidade": aluno["cidade"],
                "uf": "ES",
                "latitude": aluno["latitude"],
                "longitude": aluno["longitude"],
                "modal": aluno["modal"],
                "nascimento": date(2016, (idx % 12) + 1, min(idx + 3, 28)),
            }
            if aluno_id is None:
                aluno_id = await _scalar(
                    conn,
                    """
                    INSERT INTO sga.aluno (
                      rede_id, nome, data_nascimento, sexo, endereco, bairro, cidade, uf,
                      latitude, longitude, modal_transporte, acesso_internet, acesso_materiais, ativo
                    ) VALUES (
                      :rede_id, :nome, :nascimento, 'F', :endereco, :bairro, :cidade, :uf,
                      :latitude, :longitude, :modal, true, true, true
                    ) RETURNING id
                    """,
                    params,
                )
            else:
                await conn.execute(
                    text(
                        """
                        UPDATE sga.aluno SET
                          endereco = :endereco, bairro = :bairro, cidade = :cidade, uf = :uf,
                          latitude = :latitude, longitude = :longitude, modal_transporte = :modal,
                          acesso_internet = true, acesso_materiais = true, ativo = true
                        WHERE id = :id
                        """
                    ),
                    {**params, "id": aluno_id},
                )

            matricula = await _scalar(
                conn,
                """
                SELECT id FROM sga.matricula
                WHERE aluno_id = :aluno_id AND ano_letivo_id = :ano_id AND status = 'ATIVA'
                LIMIT 1
                """,
                {"aluno_id": aluno_id, "ano_id": ano_id},
            )
            if matricula is None:
                await conn.execute(
                    text(
                        """
                        INSERT INTO sga.matricula (rede_id, aluno_id, turma_id, ano_letivo_id, status, data_matricula)
                        VALUES (:rede_id, :aluno_id, :turma_id, :ano_id, 'ATIVA', CURRENT_DATE)
                        """
                    ),
                    {
                        "rede_id": rede_id,
                        "aluno_id": aluno_id,
                        "turma_id": turma_id,
                        "ano_id": ano_id,
                    },
                )

            resultado = await calcular_deslocamento(
                aluno["latitude"],
                aluno["longitude"],
                escola["latitude"],
                escola["longitude"],
                aluno["modal"],
            )
            await conn.execute(
                text(
                    """
                    UPDATE sga.aluno SET
                      distancia_metros = :dist,
                      tempo_deslocamento_min = :tempo,
                      metodo_distancia = :metodo
                    WHERE id = :id
                    """
                ),
                {
                    "id": aluno_id,
                    "dist": Decimal(str(resultado.distancia_metros)),
                    "tempo": resultado.tempo_minutos,
                    "metodo": resultado.metodo,
                },
            )
            print(
                f"{aluno['nome']} → {escola['nome']}: "
                f"{resultado.distancia_metros:.0f} m · {resultado.tempo_minutos} min · {resultado.metodo}"
            )

        # Chamadas demonstrativas (presenças/faltas) para o painel Deslocamento × faltas.
        # Alunos mais distantes tendem a ter mais faltas na amostra.
        print("--- frequência demonstrativa ---")
        dias = [date.today() - timedelta(days=d) for d in range(1, 11)]
        # faltas por índice de aluno (0..4): próximo → poucos; longe → mais
        faltas_por_aluno = [1, 2, 1, 3, 5]

        for idx, aluno in enumerate(ALUNOS):
            aluno_id = await _scalar(
                conn,
                "SELECT id FROM sga.aluno WHERE rede_id = :rede_id AND nome = :nome LIMIT 1",
                {"rede_id": rede_id, "nome": aluno["nome"]},
            )
            turma_id = turma_ids[aluno["escola_idx"]]
            if aluno_id is None:
                continue
            faltas_alvo = faltas_por_aluno[idx]
            for dia_i, dia in enumerate(dias):
                presente = dia_i >= faltas_alvo  # primeiros N dias = falta
                await conn.execute(
                    text(
                        """
                        INSERT INTO sga.frequencia (
                          rede_id, turma_id, aluno_id, data, ordem, presente, observacao
                        ) VALUES (
                          :rede_id, :turma_id, :aluno_id, :data, 1, :presente, :obs
                        )
                        ON CONFLICT (turma_id, aluno_id, data, ordem)
                        DO UPDATE SET presente = EXCLUDED.presente, observacao = EXCLUDED.observacao
                        """
                    ),
                    {
                        "rede_id": rede_id,
                        "turma_id": turma_id,
                        "aluno_id": aluno_id,
                        "data": dia,
                        "presente": presente,
                        "obs": None if presente else "Falta demonstrativa (carga geo ES)",
                    },
                )
            print(f"{aluno['nome']}: 10 registros · {faltas_alvo} falta(s)")

    await engine.dispose()
    print("carga_geo_es concluída.")


if __name__ == "__main__":
    asyncio.run(main())
