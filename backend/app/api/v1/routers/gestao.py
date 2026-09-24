from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_GESTAO, require_perfil
from app.db.session import get_db
from app.models.usuario import Usuario
from app.services.analitica_service import ambiente_por_bairro, estatisticas_rede

router = APIRouter(prefix="/gestao", tags=["gestao"])


@router.get("/estatisticas")
async def estatisticas(
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO, "secretaria")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await estatisticas_rede(db, usuario.rede_id)


@router.get("/professores")
async def listar_professores(
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO, "secretaria")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    rows = (
        await db.execute(
            select(Usuario).where(Usuario.rede_id == usuario.rede_id, Usuario.perfil == "professor").order_by(Usuario.nome)
        )
    ).scalars().all()
    return [
        {"id": u.id, "nome": u.nome, "email": u.email, "escola_id": u.escola_id, "perfil": u.perfil}
        for u in rows
    ]


@router.get("/ambiente-bairro")
async def dashboard_ambiente(
    bairro: str | None = Query(default=None),
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO, "secretaria")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await ambiente_por_bairro(db, usuario.rede_id, bairro)
