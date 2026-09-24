from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AlunoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    nome_social: str | None = Field(default=None, max_length=255)
    data_nascimento: date | None = None
    sexo: str | None = Field(default=None, max_length=20)
    cor_raca: str | None = Field(default=None, max_length=40)
    naturalidade_cidade: str | None = Field(default=None, max_length=120)
    naturalidade_uf: str | None = Field(default=None, max_length=2)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    nome_mae: str | None = Field(default=None, max_length=255)
    nome_pai: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    numero: str | None = Field(default=None, max_length=20)
    complemento: str | None = Field(default=None, max_length=120)
    bairro: str | None = Field(default=None, max_length=120)
    cidade: str | None = Field(default=None, max_length=120)
    uf: str | None = Field(default=None, max_length=2)
    cep: str | None = Field(default=None, max_length=12)
    latitude: float | None = None
    longitude: float | None = None
    modal_transporte: str | None = Field(default=None, max_length=40)
    acesso_internet: bool | None = None
    acesso_materiais: bool | None = None
    necessidades_especiais: str | None = None
    ativo: bool = True


class AlunoCreate(AlunoBase):
    pass


class AlunoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    nome_social: str | None = Field(default=None, max_length=255)
    data_nascimento: date | None = None
    sexo: str | None = Field(default=None, max_length=20)
    cor_raca: str | None = Field(default=None, max_length=40)
    naturalidade_cidade: str | None = Field(default=None, max_length=120)
    naturalidade_uf: str | None = Field(default=None, max_length=2)
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    nome_mae: str | None = Field(default=None, max_length=255)
    nome_pai: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    numero: str | None = Field(default=None, max_length=20)
    complemento: str | None = Field(default=None, max_length=120)
    bairro: str | None = Field(default=None, max_length=120)
    cidade: str | None = Field(default=None, max_length=120)
    uf: str | None = Field(default=None, max_length=2)
    cep: str | None = Field(default=None, max_length=12)
    latitude: float | None = None
    longitude: float | None = None
    modal_transporte: str | None = Field(default=None, max_length=40)
    acesso_internet: bool | None = None
    acesso_materiais: bool | None = None
    necessidades_especiais: str | None = None
    ativo: bool | None = None


class AlunoRead(AlunoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rede_id: int
    distancia_metros: Decimal | None = None
    tempo_deslocamento_min: int | None = None
    metodo_distancia: str | None = None
    dados_anonimizados: bool = False
