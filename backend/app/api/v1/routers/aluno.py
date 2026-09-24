from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil, scoped_select
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.schemas.aluno import AlunoCreate, AlunoRead, AlunoUpdate

router = APIRouter(prefix="/alunos", tags=["alunos"])


@router.get("", response_model=list[AlunoRead], summary="Listar alunos", description="Lista os alunos da rede do token.", responses={200: {"description": "Alunos listados com sucesso."}, 401: {"description": "Token inválido ou ausente."}})
async def listar_alunos(usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)) -> list[Aluno]:
    result = await db.execute(scoped_select(select(Aluno), usuario, Aluno).limit(limit).offset(offset))
    return result.scalars().all()


@router.get("/buscar", response_model=list[AlunoRead], summary="Buscar alunos por nome", description="Busca alunos da rede autenticada por nome.", responses={200: {"description": "Resultado da busca."}, 401: {"description": "Token inválido ou ausente."}})
async def buscar_alunos_por_nome(nome: str = Query(..., min_length=2), usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db), limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)) -> list[Aluno]:
    stmt = scoped_select(select(Aluno), usuario, Aluno).where(Aluno.nome.ilike(f"%{nome}%")).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=AlunoRead, status_code=status.HTTP_201_CREATED, summary="Cadastrar aluno", description="Cria um aluno na rede do token.", responses={201: {"description": "Aluno criado com sucesso."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def criar_aluno(payload: AlunoCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Aluno:
    aluno = Aluno(**payload.model_dump(), rede_id=usuario.rede_id)
    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)
    return aluno


@router.get("/{aluno_id}", response_model=AlunoRead, summary="Obter aluno", description="Busca um aluno do tenant autenticado.", responses={200: {"description": "Aluno encontrado."}, 404: {"description": "Aluno não encontrado."}, 401: {"description": "Token inválido ou ausente."}})
async def obter_aluno(aluno_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Aluno:
    return await get_owned(db, Aluno, aluno_id, usuario, "Aluno não encontrado.")


@router.put("/{aluno_id}", response_model=AlunoRead, summary="Atualizar aluno", description="Atualiza um aluno da rede do token.", responses={200: {"description": "Aluno atualizado com sucesso."}, 404: {"description": "Aluno não encontrado."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def atualizar_aluno(aluno_id: int, payload: AlunoUpdate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Aluno:
    aluno = await get_owned(db, Aluno, aluno_id, usuario, "Aluno não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(aluno, field, value)
    await db.commit()
    await db.refresh(aluno)
    return aluno
