from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Frequencia(Base):
    __tablename__ = "frequencia"
    __table_args__ = (
        UniqueConstraint("turma_id", "aluno_id", "data", "ordem", name="idx_frequencia_idempotencia"),
        {"schema": "sga"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), index=True)
    turma_id: Mapped[int] = mapped_column(ForeignKey("sga.turma.id"), index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), index=True)
    data: Mapped[date] = mapped_column(Date)
    ordem: Mapped[int] = mapped_column(Integer, default=1)
    presente: Mapped[bool] = mapped_column(Boolean)
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    registrada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    aluno: Mapped["Aluno"] = relationship()
