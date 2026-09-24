from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.usuario import Usuario
from app.schemas.responsavel import ResponsavelCreate, ResponsavelRead, ResponsavelUpdate

router = APIRouter(prefix="/responsaveis", tags=["responsaveis"])


@router.get("", response_model=list[ResponsavelRead])
async def listar_responsaveis(
    aluno_id: int | None = Query(default=None),
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Responsavel]:
    stmt = select(Responsavel).where(Responsavel.rede_id == usuario.rede_id)
    if aluno_id is not None:
        stmt = stmt.where(Responsavel.aluno_id == aluno_id)
    return (await db.execute(stmt)).scalars().all()


@router.post("", response_model=ResponsavelRead, status_code=status.HTTP_201_CREATED)
async def criar_responsavel(
    payload: ResponsavelCreate,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)),
    db: AsyncSession = Depends(get_db),
) -> Responsavel:
    await get_owned(db, Aluno, payload.aluno_id, usuario, "Aluno não encontrado.")
    item = Responsavel(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{responsavel_id}", response_model=ResponsavelRead)
async def atualizar_responsavel(
    responsavel_id: int,
    payload: ResponsavelUpdate,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)),
    db: AsyncSession = Depends(get_db),
) -> Responsavel:
    item = await get_owned(db, Responsavel, responsavel_id, usuario, "Responsável não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
