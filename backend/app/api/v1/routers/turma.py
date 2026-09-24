from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil, scoped_select
from app.db.session import get_db
from app.models.ano_letivo import AnoLetivo
from app.models.escola import Escola
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.schemas.turma import TurmaCreate, TurmaRead, TurmaUpdate

router = APIRouter(prefix="/turmas", tags=["turmas"])


@router.get("", response_model=list[TurmaRead], summary="Listar turmas", description="Lista as turmas da rede do token.", responses={200: {"description": "Turmas listadas com sucesso."}, 401: {"description": "Token inválido ou ausente."}})
async def listar_turmas(usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[Turma]:
    result = await db.execute(scoped_select(select(Turma), usuario, Turma).limit(limit).offset(offset))
    return result.scalars().all()


@router.post("", response_model=TurmaRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar turma", description="Cria uma turma na escola e no ano letivo da mesma rede do token.", responses={201: {"description": "Turma criada com sucesso."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}, 404: {"description": "Escola ou ano letivo não encontrado."}})
async def criar_turma(payload: TurmaCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Turma:
    await get_owned(db, Escola, payload.escola_id, usuario, "Escola não encontrada.")
    await get_owned(db, AnoLetivo, payload.ano_letivo_id, usuario, "Ano letivo não encontrado.")
    turma = Turma(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(turma)
    await db.commit()
    await db.refresh(turma)
    return turma


@router.get("/{turma_id}", response_model=TurmaRead, summary="Obter turma", description="Busca uma turma do tenant autenticado.", responses={200: {"description": "Turma encontrada."}, 404: {"description": "Turma não encontrada."}, 401: {"description": "Token inválido ou ausente."}})
async def obter_turma(turma_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Turma:
    return await get_owned(db, Turma, turma_id, usuario, "Turma não encontrada.")


@router.put("/{turma_id}", response_model=TurmaRead, summary="Atualizar turma", description="Atualiza os dados da turma da rede do token.", responses={200: {"description": "Turma atualizada com sucesso."}, 404: {"description": "Turma não encontrada."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def atualizar_turma(turma_id: int, payload: TurmaUpdate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Turma:
    turma = await get_owned(db, Turma, turma_id, usuario, "Turma não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(turma, field, value)
    await db.commit()
    await db.refresh(turma)
    return turma
