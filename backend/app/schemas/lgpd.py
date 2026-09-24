from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsentimentoCreate(BaseModel):
    aluno_id: int
    responsavel_id: int | None = None
    tipo: str = Field(default="tratamento_dados", max_length=80)
    finalidade: str | None = None
    concedido: bool = True


class ConsentimentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
    aluno_id: int
    responsavel_id: int | None
    tipo: str
    finalidade: str | None
    concedido: bool
    data_registro: datetime
    registrado_por: str | None


class AnonimizarRequest(BaseModel):
    confirmar: bool = False
