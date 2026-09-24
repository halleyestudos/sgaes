from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.historico_escolar import HistoricoEscolar
from app.models.usuario import Usuario
from app.schemas.historico_escolar import HistoricoEscolarCreate, HistoricoEscolarRead, HistoricoEscolarUpdate

router = APIRouter(prefix="/historicos-escolares", tags=["historicos-escolares"])


@router.get("", response_model=list[HistoricoEscolarRead])
async def listar_historicos(
    aluno_id: int | None = Query(default=None),
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HistoricoEscolar]:
    stmt = select(HistoricoEscolar).where(HistoricoEscolar.rede_id == usuario.rede_id)
    if aluno_id is not None:
        stmt = stmt.where(HistoricoEscolar.aluno_id == aluno_id)
    return (await db.execute(stmt.order_by(HistoricoEscolar.ultima_escola.desc(), HistoricoEscolar.ano.desc()))).scalars().all()


@router.post("", response_model=HistoricoEscolarRead, status_code=status.HTTP_201_CREATED)
async def criar_historico(
    payload: HistoricoEscolarCreate,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)),
    db: AsyncSession = Depends(get_db),
) -> HistoricoEscolar:
    await get_owned(db, Aluno, payload.aluno_id, usuario, "Aluno não encontrado.")
    if payload.ultima_escola:
        await db.execute(
            update(HistoricoEscolar)
            .where(HistoricoEscolar.aluno_id == payload.aluno_id, HistoricoEscolar.rede_id == usuario.rede_id)
            .values(ultima_escola=False)
        )
    item = HistoricoEscolar(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{historico_id}", response_model=HistoricoEscolarRead)
async def atualizar_historico(
    historico_id: int,
    payload: HistoricoEscolarUpdate,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)),
    db: AsyncSession = Depends(get_db),
) -> HistoricoEscolar:
    item = await get_owned(db, HistoricoEscolar, historico_id, usuario, "Histórico não encontrado.")
    data = payload.model_dump(exclude_unset=True)
    if data.get("ultima_escola"):
        await db.execute(
            update(HistoricoEscolar)
            .where(HistoricoEscolar.aluno_id == item.aluno_id, HistoricoEscolar.rede_id == usuario.rede_id)
            .values(ultima_escola=False)
        )
    for field, value in data.items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
