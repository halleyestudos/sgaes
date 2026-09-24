from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AlertaFrequencia(Base):
    __tablename__ = "alerta_frequencia"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), index=True)
    ano_letivo_id: Mapped[int] = mapped_column(ForeignKey("sga.ano_letivo.id"), index=True)
    nivel: Mapped[str] = mapped_column(String(30))
    percentual: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolvido: Mapped[bool] = mapped_column(Boolean, default=False)
