from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ChamadaItem(BaseModel):
    aluno_id: int
    presente: bool
    observacao: str | None = Field(default=None, max_length=255)


class ChamadaCreate(BaseModel):
    turma_id: int
    data: date
    ordem: int = Field(default=1, ge=1)
    itens: list[ChamadaItem] = Field(min_length=1)


class ChamadaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    turma_id: int
    aluno_id: int
    data: date
    ordem: int
    presente: bool
    observacao: str | None


class FrequenciaConsolidada(BaseModel):
    aluno_id: int
    nome: str
    aulas: int
    presencas: int
    faltas: int
    percentual: Decimal
    nivel_alerta: str | None = None


class ChamadaDiaItem(BaseModel):
    aluno_id: int
    nome: str
    presente: bool
    observacao: str | None = None
    registrada: bool = False


class AlertaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    aluno_id: int
    ano_letivo_id: int
    nivel: str
    percentual: Decimal
    resolvido: bool
