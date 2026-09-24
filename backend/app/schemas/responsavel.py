from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResponsavelBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    parentesco: str | None = Field(default=None, max_length=60)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    cpf: str | None = Field(default=None, max_length=14)
    principal: bool = True


class ResponsavelCreate(ResponsavelBase):
    aluno_id: int


class ResponsavelUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    parentesco: str | None = Field(default=None, max_length=60)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    cpf: str | None = Field(default=None, max_length=14)
    principal: bool | None = None


class ResponsavelRead(ResponsavelBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
    aluno_id: int
