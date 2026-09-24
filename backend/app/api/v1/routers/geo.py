from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, PERFIS_GESTAO, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.escola import Escola
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.services.analitica_service import correlacao_deslocamento_faltas
from app.services.geo_service import calcular_deslocamento

router = APIRouter(prefix="/geo", tags=["geo"])


class CalcularDeslocamentoRequest(BaseModel):
    aluno_id: int
    modal_transporte: str | None = Field(default=None, max_length=40)
    persistir: bool = True


@router.post("/deslocamento")
async def calcular_e_gravar_deslocamento(
    payload: CalcularDeslocamentoRequest,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO, *PERFIS_GESTAO)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    aluno = await get_owned(db, Aluno, payload.aluno_id, usuario, "Aluno não encontrado.")
    if aluno.latitude is None or aluno.longitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno sem coordenadas de residência.")

    matricula = (
        await db.execute(
            select(Matricula)
            .where(Matricula.aluno_id == aluno.id, Matricula.status == "ATIVA", Matricula.rede_id == usuario.rede_id)
            .limit(1)
        )
    ).scalar_one_or_none()
    if matricula is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno sem matrícula ativa.")

    turma = await get_owned(db, Turma, matricula.turma_id, usuario, "Turma não encontrada.")
    escola = await get_owned(db, Escola, turma.escola_id, usuario, "Escola não encontrada.")
    if escola.latitude is None or escola.longitude is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escola sem coordenadas.")

    modal = payload.modal_transporte or aluno.modal_transporte or "a_pe"
    lat_o, lon_o = float(aluno.latitude), float(aluno.longitude)
    lat_d, lon_d = float(escola.latitude), float(escola.longitude)
    resultado = await calcular_deslocamento(lat_o, lon_o, lat_d, lon_d, modal)

    if payload.persistir:
        aluno.distancia_metros = Decimal(str(resultado.distancia_metros))
        aluno.tempo_deslocamento_min = resultado.tempo_minutos
        aluno.metodo_distancia = resultado.metodo
        aluno.modal_transporte = resultado.modal
        await db.commit()
        await db.refresh(aluno)

    return {
        "aluno_id": aluno.id,
        "escola_id": escola.id,
        "escola_nome": escola.nome,
        "origem": {"latitude": lat_o, "longitude": lon_o},
        "destino": {"latitude": lat_d, "longitude": lon_d},
        "distancia_metros": resultado.distancia_metros,
        "tempo_deslocamento_min": resultado.tempo_minutos,
        "metodo": resultado.metodo,
        "modal": resultado.modal,
        # GeoJSON LineString coordinates: [lon, lat]
        "geometria": resultado.geometria,
        "mapa_osm_url": (
            "https://www.openstreetmap.org/directions?"
            f"engine=fossgis_osrm_car&route={lat_o}%2C{lon_o}%3B{lat_d}%2C{lon_d}"
        ),
    }


@router.get("/correlacao-faltas")
async def correlacao_faltas(
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO, "secretaria")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await correlacao_deslocamento_faltas(db, usuario.rede_id)
