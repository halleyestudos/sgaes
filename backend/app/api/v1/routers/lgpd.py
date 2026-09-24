from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, PERFIS_GESTAO, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.consentimento_lgpd import ConsentimentoLgpd
from app.models.responsavel import Responsavel
from app.models.usuario import Usuario
from app.schemas.lgpd import AnonimizarRequest, ConsentimentoCreate, ConsentimentoRead
from app.services.lgpd_service import anonimizar_aluno, aplicar_mascara_aluno

router = APIRouter(prefix="/lgpd", tags=["lgpd"])


@router.get("/consentimentos", response_model=list[ConsentimentoRead])
async def listar_consentimentos(
    aluno_id: int | None = Query(default=None),
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConsentimentoLgpd]:
    stmt = select(ConsentimentoLgpd).where(ConsentimentoLgpd.rede_id == usuario.rede_id)
    if aluno_id is not None:
        stmt = stmt.where(ConsentimentoLgpd.aluno_id == aluno_id)
    return (await db.execute(stmt)).scalars().all()


@router.post("/consentimentos", response_model=ConsentimentoRead, status_code=status.HTTP_201_CREATED)
async def registrar_consentimento(
    payload: ConsentimentoCreate,
    usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)),
    db: AsyncSession = Depends(get_db),
) -> ConsentimentoLgpd:
    await get_owned(db, Aluno, payload.aluno_id, usuario, "Aluno não encontrado.")
    if payload.responsavel_id is not None:
        await get_owned(db, Responsavel, payload.responsavel_id, usuario, "Responsável não encontrado.")
    item = ConsentimentoLgpd(
        **payload.model_dump(),
        rede_id=usuario.rede_id,
        registrado_por=usuario.email,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/alunos/{aluno_id}/mascarado")
async def aluno_mascarado(
    aluno_id: int,
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO, "secretaria")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    aluno = await get_owned(db, Aluno, aluno_id, usuario, "Aluno não encontrado.")
    return aplicar_mascara_aluno(aluno)


@router.post("/alunos/{aluno_id}/anonimizar")
async def anonimizar(
    aluno_id: int,
    payload: AnonimizarRequest,
    usuario: Usuario = Depends(require_perfil(*PERFIS_GESTAO)),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not payload.confirmar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Confirme a anonimização com confirmar=true.")
    aluno = await get_owned(db, Aluno, aluno_id, usuario, "Aluno não encontrado.")
    anonimizar_aluno(aluno)
    await db.commit()
    return {"aluno_id": aluno.id, "dados_anonimizados": True, "nome": aluno.nome}
