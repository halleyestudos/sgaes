from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenError, decode_access_token
from app.core.tenancy import set_tenant
from app.db.session import get_db
from app.models.usuario import Usuario

bearer_scheme = HTTPBearer(auto_error=False)

PERFIS_CADASTRO = {"administrador", "gestor", "diretor", "secretaria"}
PERFIS_FREQUENCIA = {"administrador", "gestor", "diretor", "secretaria", "professor"}
PERFIS_GESTAO = {"administrador", "gestor", "diretor"}


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Informe o token de acesso.")
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    try:
        usuario_id = int(payload["sub"])
        rede_id = int(payload["rede_id"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.") from exc

    usuario = await db.get(Usuario, usuario_id)
    if usuario is None or usuario.rede_id != rede_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.")
    await set_tenant(usuario.rede_id, db)
    return usuario


def require_perfil(*perfis: str):
    permitidos = set(perfis)

    async def checker(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if usuario.perfil not in permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seu perfil não pode executar esta ação.")
        return usuario

    return checker


async def get_owned(db: AsyncSession, model, obj_id: int, usuario: Usuario, detalhe: str):
    obj = await db.get(model, obj_id)
    if obj is None or getattr(obj, "rede_id", None) != usuario.rede_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detalhe)
    return obj


def scoped_select(stmt: Select, usuario: Usuario, model) -> Select:
    stmt = stmt.where(model.rede_id == usuario.rede_id)
    escola_id = getattr(model, "escola_id", None)
    if escola_id is not None and usuario.escola_id is not None and usuario.perfil in {"professor", "diretor"}:
        stmt = stmt.where(model.escola_id == usuario.escola_id)
    return stmt
