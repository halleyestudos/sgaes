from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Aluno(Base):
    __tablename__ = "aluno"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_social: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cor_raca: Mapped[str | None] = mapped_column(String(40), nullable=True)
    naturalidade_cidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    naturalidade_uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_mae: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nome_pai: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(12), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    modal_transporte: Mapped[str | None] = mapped_column(String(40), nullable=True)
    distancia_metros: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    tempo_deslocamento_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metodo_distancia: Mapped[str | None] = mapped_column(String(40), nullable=True)
    acesso_internet: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    acesso_materiais: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    necessidades_especiais: Mapped[str | None] = mapped_column(Text, nullable=True)
    dados_anonimizados: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    rede: Mapped["Rede"] = relationship(back_populates="alunos")
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="aluno")
    responsaveis: Mapped[list["Responsavel"]] = relationship(back_populates="aluno")
    historicos_escolares: Mapped[list["HistoricoEscolar"]] = relationship(back_populates="aluno")
    consentimentos: Mapped[list["ConsentimentoLgpd"]] = relationship(back_populates="aluno")
