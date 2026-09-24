from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HistoricoEscolarBase(BaseModel):
    nome_escola: str = Field(..., min_length=2, max_length=255)
    codigo_inep: str | None = Field(default=None, max_length=20)
    ano: int | None = None
    serie: str | None = Field(default=None, max_length=40)
    ultima_escola: bool = False
    observacao: str | None = None


class HistoricoEscolarCreate(HistoricoEscolarBase):
    aluno_id: int


class HistoricoEscolarUpdate(BaseModel):
    nome_escola: str | None = Field(default=None, min_length=2, max_length=255)
    codigo_inep: str | None = Field(default=None, max_length=20)
    ano: int | None = None
    serie: str | None = Field(default=None, max_length=40)
    ultima_escola: bool | None = None
    observacao: str | None = None


class HistoricoEscolarRead(HistoricoEscolarBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
    aluno_id: int
