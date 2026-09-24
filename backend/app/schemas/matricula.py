from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MatriculaCreate(BaseModel):
    aluno_id: int
    turma_id: int
    ano_letivo_id: int
    data_matricula: date | None = None


class MatriculaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rede_id: int
    aluno_id: int
    turma_id: int
    ano_letivo_id: int
    status: str
    data_matricula: date
    data_encerramento: date | None
    motivo_encerramento: str | None


class TransferenciaCreate(BaseModel):
    nova_turma_id: int
    motivo: str | None = Field(default=None, max_length=255)


class EncerramentoCreate(BaseModel):
    motivo: str = Field(..., min_length=3, max_length=255)


class AlunoTurmaRead(BaseModel):
    aluno_id: int
    nome: str
    matricula_id: int
    status: str
