from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TurmaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    serie: str | None = Field(default=None, max_length=20)
    turno: str | None = Field(default=None, max_length=20)
    professor_id: int | None = None
    oferece_merenda: bool = True
    apoio_pedagogico: bool = False
    ativa: bool = True


class TurmaCreate(TurmaBase):
    escola_id: int
    ano_letivo_id: int


class TurmaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    serie: str | None = Field(default=None, max_length=20)
    turno: str | None = Field(default=None, max_length=20)
    professor_id: int | None = None
    oferece_merenda: bool | None = None
    apoio_pedagogico: bool | None = None
    ativa: bool | None = None


class TurmaRead(TurmaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
    escola_id: int
    ano_letivo_id: int
