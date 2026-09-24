from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EscolaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    codigo_inep: str | None = Field(default=None, max_length=20)
    dependencia_administrativa: str | None = Field(default=None, max_length=40)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    bairro: str | None = Field(default=None, max_length=120)
    cidade: str | None = Field(default=None, max_length=120)
    uf: str | None = Field(default=None, max_length=2)
    cep: str | None = Field(default=None, max_length=12)
    latitude: float | None = None
    longitude: float | None = None
    ativo: bool = True


class EscolaCreate(EscolaBase):
    pass


class EscolaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    codigo_inep: str | None = Field(default=None, max_length=20)
    dependencia_administrativa: str | None = Field(default=None, max_length=40)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    bairro: str | None = Field(default=None, max_length=120)
    cidade: str | None = Field(default=None, max_length=120)
    uf: str | None = Field(default=None, max_length=2)
    cep: str | None = Field(default=None, max_length=12)
    latitude: float | None = None
    longitude: float | None = None
    ativo: bool | None = None


class EscolaRead(EscolaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
