from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class NivelFrequencia:
    nivel: str | None
    percentual: Decimal


def calcular_nivel_alerta(presencas: int, aulas: int) -> NivelFrequencia:
    if aulas <= 0:
        return NivelFrequencia(None, Decimal("100.00"))
    percentual = (Decimal(presencas) / Decimal(aulas) * Decimal("100")).quantize(Decimal("0.01"))
    if percentual < Decimal("30"):
        return NivelFrequencia("LIMITE_LEGAL_30", percentual)
    if percentual < Decimal("75"):
        return NivelFrequencia("RISCO_ABANDONO", percentual)
    return NivelFrequencia(None, percentual)
