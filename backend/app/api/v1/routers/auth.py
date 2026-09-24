from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioPublico

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(usuario: Usuario) -> TokenResponse:
    settings = get_settings()
    token = create_access_token(sub=str(usuario.id), rede_id=usuario.rede_id, perfil=usuario.perfil, escola_id=usuario.escola_id)
    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
        usuario=UsuarioPublico.model_validate(usuario),
    )


@router.post("/login", response_model=TokenResponse, summary="Entrar", description="Autentica o usuário e devolve um JWT com rede, perfil e escola.", responses={200: {"description": "Sessão iniciada."}, 401: {"description": "Credenciais inválidas."}})
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    usuario = await db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))
    if usuario is None or not verify_password(payload.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")
    return _token_response(usuario)


@router.post("/refresh", response_model=TokenResponse, summary="Renovar token", description="Emite um novo JWT para o usuário autenticado.", responses={200: {"description": "Token renovado."}, 401: {"description": "Token inválido ou ausente."}})
async def refresh(usuario: Usuario = Depends(get_current_user)) -> TokenResponse:
    return _token_response(usuario)


@router.get("/me", response_model=UsuarioPublico, summary="Usuário atual", description="Retorna o perfil associado ao token.", responses={200: {"description": "Usuário autenticado."}, 401: {"description": "Token inválido ou ausente."}})
async def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario
