from __future__ import annotations

from app.models.aluno import Aluno


def mascarar_texto(valor: str | None, manter: int = 3) -> str | None:
    if not valor:
        return valor
    if len(valor) <= manter:
        return "*" * len(valor)
    return valor[:manter] + "*" * (len(valor) - manter)


def mascarar_coordenada(valor: float | None, precisao: int = 2) -> float | None:
    """Reduz precisão geográfica (~1 km) para análise agregada."""
    if valor is None:
        return None
    fator = 10**precisao
    return round(valor * fator) / fator


def aplicar_mascara_aluno(aluno: Aluno) -> dict:
    return {
        "id": aluno.id,
        "nome": mascarar_texto(aluno.nome, 2),
        "telefone": mascarar_texto(aluno.telefone, 4),
        "email": mascarar_texto(aluno.email, 2),
        "endereco": mascarar_texto(aluno.endereco, 5),
        "numero": "***" if aluno.numero else None,
        "bairro": aluno.bairro,
        "cidade": aluno.cidade,
        "uf": aluno.uf,
        "cep": mascarar_texto(aluno.cep, 2),
        "latitude": mascarar_coordenada(aluno.latitude),
        "longitude": mascarar_coordenada(aluno.longitude),
        "dados_anonimizados": aluno.dados_anonimizados,
    }


def anonimizar_aluno(aluno: Aluno) -> None:
    aluno.nome = f"Aluno anonimizado {aluno.id}"
    aluno.nome_social = None
    aluno.telefone = None
    aluno.email = None
    aluno.nome_mae = None
    aluno.nome_pai = None
    aluno.endereco = None
    aluno.numero = None
    aluno.complemento = None
    aluno.cep = None
    aluno.latitude = mascarar_coordenada(aluno.latitude)
    aluno.longitude = mascarar_coordenada(aluno.longitude)
    aluno.dados_anonimizados = True
