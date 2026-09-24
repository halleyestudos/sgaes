from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil, scoped_select
from app.db.session import get_db
from app.models.escola import Escola
from app.models.usuario import Usuario
from app.schemas.escola import EscolaCreate, EscolaRead, EscolaUpdate

router = APIRouter(prefix="/escolas", tags=["escolas"])


@router.get("", response_model=list[EscolaRead], summary="Listar escolas", description="Lista as escolas da rede do usuário autenticado.", responses={200: {"description": "Escolas listadas com sucesso."}, 401: {"description": "Token inválido ou ausente."}})
async def listar_escolas(usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[Escola]:
    stmt = scoped_select(select(Escola), usuario, Escola).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=EscolaRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar escola", description="Cria uma nova escola na rede do token.", responses={201: {"description": "Escola criada com sucesso."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def criar_escola(payload: EscolaCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Escola:
    escola = Escola(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(escola)
    await db.commit()
    await db.refresh(escola)
    return escola


@router.get("/{escola_id}", response_model=EscolaRead, summary="Obter escola", description="Busca uma escola do tenant autenticado.", responses={200: {"description": "Escola encontrada."}, 404: {"description": "Escola não encontrada."}, 401: {"description": "Token inválido ou ausente."}})
async def obter_escola(escola_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Escola:
    return await get_owned(db, Escola, escola_id, usuario, "Escola não encontrada.")


@router.put("/{escola_id}", response_model=EscolaRead, summary="Atualizar escola", description="Atualiza uma escola da rede do token.", responses={200: {"description": "Escola atualizada com sucesso."}, 404: {"description": "Escola não encontrada."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def atualizar_escola(escola_id: int, payload: EscolaUpdate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Escola:
    escola = await get_owned(db, Escola, escola_id, usuario, "Escola não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(escola, field, value)
    await db.commit()
    await db.refresh(escola)
    return escola
