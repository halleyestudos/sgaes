from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Responsavel(Base):
    __tablename__ = "responsavel"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    parentesco: Mapped[str | None] = mapped_column(String(60), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="responsaveis")
