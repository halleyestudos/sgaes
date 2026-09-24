from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Matricula(Base):
    __tablename__ = "matricula"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), index=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("sga.turma.id"), index=True)
    ano_letivo_id: Mapped[int] = mapped_column(ForeignKey("sga.ano_letivo.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="ATIVA")
    data_matricula: Mapped[date] = mapped_column(Date, default=date.today)
    data_encerramento: Mapped[date | None] = mapped_column(Date, nullable=True)
    motivo_encerramento: Mapped[str | None] = mapped_column(String(255), nullable=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="matriculas")
    turma: Mapped["Turma"] = relationship(back_populates="matriculas")
