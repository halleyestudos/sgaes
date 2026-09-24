from __future__ import annotations

from app.models.turma import Turma
from app.repositories.base import BaseRepository


class TurmaRepository(BaseRepository):
    model = Turma
