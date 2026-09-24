from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/modulos-futuros", tags=["modulos-futuros"])

MODULOS = [
    {
        "codigo": "trabalho_docente",
        "titulo": "Condições do trabalho docente",
        "descricao": "Questionários anônimos sobre deslocamento, carga horária e suporte pedagógico.",
        "status": "em_breve",
    },
    {
        "codigo": "infraestrutura_higiene",
        "titulo": "Infraestrutura e higiene escolar",
        "descricao": "Vistorias de conservação, banheiros, iluminação e espaço por aluno.",
        "status": "em_breve",
    },
    {
        "codigo": "desburocratizacao",
        "titulo": "Desburocratização administrativa",
        "descricao": "Rotinas que liberam tempo pedagógico e simplificam a secretaria.",
        "status": "em_breve",
    },
]


@router.get("")
async def listar_modulos_futuros() -> list[dict]:
    return MODULOS
