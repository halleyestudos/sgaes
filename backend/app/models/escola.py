from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Escola(Base):
    __tablename__ = "escola"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo_inep: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dependencia_administrativa: Mapped[str | None] = mapped_column(String(40), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(12), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    rede: Mapped["Rede"] = relationship(back_populates="escolas")
    turmas: Mapped[list["Turma"]] = relationship(back_populates="escola")
