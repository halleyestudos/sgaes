from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConsentimentoLgpd(Base):
    __tablename__ = "consentimento_lgpd"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), nullable=False, index=True)
    responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("sga.responsavel.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False, default="tratamento_dados")
    finalidade: Mapped[str | None] = mapped_column(Text, nullable=True)
    concedido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    data_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    registrado_por: Mapped[str | None] = mapped_column(String(255), nullable=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="consentimentos")
