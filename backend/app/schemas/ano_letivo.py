from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AnoLetivoBase(BaseModel):
    nome: str = Field(..., min_length=4, max_length=20)
    ativo: bool = True


class AnoLetivoCreate(AnoLetivoBase):
    pass


class AnoLetivoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=4, max_length=20)
    ativo: bool | None = None


class AnoLetivoRead(AnoLetivoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
