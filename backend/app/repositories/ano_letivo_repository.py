from __future__ import annotations

from app.models.ano_letivo import AnoLetivo
from app.repositories.base import BaseRepository


class AnoLetivoRepository(BaseRepository):
    model = AnoLetivo
