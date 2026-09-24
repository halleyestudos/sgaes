from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Turma(Base):
    __tablename__ = "turma"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    escola_id: Mapped[int] = mapped_column(ForeignKey("sga.escola.id"), nullable=False, index=True)
    ano_letivo_id: Mapped[int] = mapped_column(ForeignKey("sga.ano_letivo.id"), nullable=False, index=True)
    professor_id: Mapped[int | None] = mapped_column(ForeignKey("sga.usuario.id"), nullable=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    serie: Mapped[str | None] = mapped_column(String(20), nullable=True)
    turno: Mapped[str | None] = mapped_column(String(20), nullable=True)
    oferece_merenda: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    apoio_pedagogico: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    rede: Mapped["Rede"] = relationship(back_populates="turmas")
    escola: Mapped["Escola"] = relationship(back_populates="turmas")
    ano_letivo: Mapped["AnoLetivo"] = relationship(back_populates="turmas")
    professor: Mapped["Usuario | None"] = relationship(foreign_keys=[professor_id])
    matriculas: Mapped[list["Matricula"]] = relationship(back_populates="turma")
