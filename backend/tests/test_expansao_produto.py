from __future__ import annotations

from app.services.geo_service import estimar_tempo_minutos, haversine_metros
from app.services.lgpd_service import mascarar_coordenada, mascarar_texto


def test_haversine_positive():
    dist = haversine_metros(-15.7942, -47.8822, -15.8000, -47.8900)
    assert dist > 500


def test_tempo_modal():
    assert estimar_tempo_minutos(4500, "a_pe") >= 50
    assert estimar_tempo_minutos(4500, "onibus_escolar") < estimar_tempo_minutos(4500, "a_pe")


def test_mascara_lgpd():
    assert mascarar_texto("Maria Silva", 2) == "Ma*********"
    assert mascarar_coordenada(-15.7942, 2) == -15.79
