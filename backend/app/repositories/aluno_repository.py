from __future__ import annotations

from sqlalchemy import select

from app.models.aluno import Aluno
from app.repositories.base import BaseRepository


class AlunoRepository(BaseRepository):
    model = Aluno

    async def buscar_por_nome(self, nome: str, *, limit: int = 20, offset: int = 0) -> list[Aluno]:
        stmt = select(self.model).where(self.model.nome.ilike(f"%{nome}%")).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
