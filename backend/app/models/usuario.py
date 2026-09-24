from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "sga"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rede_id: Mapped[int] = mapped_column(ForeignKey("sga.rede.id"), nullable=False, index=True)
    escola_id: Mapped[int | None] = mapped_column(ForeignKey("sga.escola.id"), nullable=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False)

    rede: Mapped["Rede"] = relationship()
    escola: Mapped["Escola | None"] = relationship()
