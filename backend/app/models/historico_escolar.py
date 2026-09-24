from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HistoricoEscolar(Base):
    __tablename__ = "historico_escolar"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("sga.aluno.id"), nullable=False, index=True)
    nome_escola: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo_inep: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serie: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ultima_escola: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="historicos_escolares")
