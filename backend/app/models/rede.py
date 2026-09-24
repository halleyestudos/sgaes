from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Rede(Base):
    __tablename__ = "rede"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    escolas: Mapped[list["Escola"]] = relationship(back_populates="rede")
    anos_letivos: Mapped[list["AnoLetivo"]] = relationship(back_populates="rede")
    turmas: Mapped[list["Turma"]] = relationship(back_populates="rede")
    alunos: Mapped[list["Aluno"]] = relationship(back_populates="rede")
