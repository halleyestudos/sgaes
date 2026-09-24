from __future__ import annotations

import math
from dataclasses import dataclass

import httpx

MODAL_VELOCIDADE_KMH = {
    "a_pe": 4.5,
    "onibus_escolar": 25.0,
    "transporte_publico": 20.0,
    "bicicleta": 12.0,
    "outro": 15.0,
}

OSRM_URL = "https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"


@dataclass
class ResultadoDeslocamento:
    distancia_metros: float
    tempo_minutos: int
    metodo: str
    modal: str


def haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    raio = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * raio * math.asin(math.sqrt(a))


def estimar_tempo_minutos(distancia_metros: float, modal: str) -> int:
    velocidade = MODAL_VELOCIDADE_KMH.get(modal, MODAL_VELOCIDADE_KMH["outro"])
    horas = (distancia_metros / 1000.0) / velocidade
    return max(1, int(round(horas * 60)))


async def distancia_viaria_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> tuple[float, str]:
    """Distância por malha viária via OSRM; fallback Haversine × 1.35 (fator de ruas)."""
    url = OSRM_URL.format(lon1=lon1, lat1=lat1, lon2=lon2, lat2=lat2)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes") or []
                if routes:
                    return float(routes[0]["distance"]), "osrm_malha_viaria"
    except Exception:
        pass
    return haversine_metros(lat1, lon1, lat2, lon2) * 1.35, "haversine_ajustado"


async def calcular_deslocamento(
    lat_origem: float,
    lon_origem: float,
    lat_destino: float,
    lon_destino: float,
    modal: str = "a_pe",
) -> ResultadoDeslocamento:
    distancia, metodo = await distancia_viaria_metros(lat_origem, lon_origem, lat_destino, lon_destino)
    modal_norm = modal if modal in MODAL_VELOCIDADE_KMH else "outro"
    return ResultadoDeslocamento(
        distancia_metros=round(distancia, 2),
        tempo_minutos=estimar_tempo_minutos(distancia, modal_norm),
        metodo=metodo,
        modal=modal_norm,
    )
