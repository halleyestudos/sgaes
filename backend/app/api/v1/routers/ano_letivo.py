from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil, scoped_select
from app.db.session import get_db
from app.models.ano_letivo import AnoLetivo
from app.models.usuario import Usuario
from app.schemas.ano_letivo import AnoLetivoCreate, AnoLetivoRead, AnoLetivoUpdate

router = APIRouter(prefix="/anos-letivos", tags=["anos-letivos"])


@router.get("", response_model=list[AnoLetivoRead], summary="Listar anos letivos", description="Lista os anos letivos da rede do token.", responses={200: {"description": "Anos letivos listados com sucesso."}, 401: {"description": "Token inválido ou ausente."}})
async def listar_anos_letivos(usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[AnoLetivo]:
    result = await db.execute(scoped_select(select(AnoLetivo), usuario, AnoLetivo).limit(limit).offset(offset))
    return result.scalars().all()


@router.post("", response_model=AnoLetivoRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar ano letivo", description="Cria um ano letivo na rede do token.", responses={201: {"description": "Ano letivo criado com sucesso."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def criar_ano_letivo(payload: AnoLetivoCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> AnoLetivo:
    ano = AnoLetivo(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(ano)
    await db.commit()
    await db.refresh(ano)
    return ano


@router.get("/{ano_letivo_id}", response_model=AnoLetivoRead, summary="Obter ano letivo", description="Busca o ano letivo do tenant autenticado.", responses={200: {"description": "Ano letivo encontrado."}, 404: {"description": "Ano letivo não encontrado."}, 401: {"description": "Token inválido ou ausente."}})
async def obter_ano_letivo(ano_letivo_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> AnoLetivo:
    return await get_owned(db, AnoLetivo, ano_letivo_id, usuario, "Ano letivo não encontrado.")


@router.put("/{ano_letivo_id}", response_model=AnoLetivoRead, summary="Atualizar ano letivo", description="Atualiza um ano letivo da rede do token.", responses={200: {"description": "Ano letivo atualizado com sucesso."}, 404: {"description": "Ano letivo não encontrado."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def atualizar_ano_letivo(ano_letivo_id: int, payload: AnoLetivoUpdate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> AnoLetivo:
    ano = await get_owned(db, AnoLetivo, ano_letivo_id, usuario, "Ano letivo não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ano, field, value)
    await db.commit()
    await db.refresh(ano)
    return ano
