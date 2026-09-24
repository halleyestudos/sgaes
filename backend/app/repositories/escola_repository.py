from __future__ import annotations

from app.models.escola import Escola
from app.repositories.base import BaseRepository


class EscolaRepository(BaseRepository):
    model = Escola
