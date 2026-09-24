from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from jose import JWTError, jwt

from app.core.config import get_settings

ph = PasswordHasher()


class TokenError(Exception):
    pass


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except Exception:
        return False


def create_access_token(*, sub: str, rede_id: int, perfil: str, escola_id: int | None = None, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    utc_now = datetime.now(timezone.utc)
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)

    payload: dict[str, Any] = {
        "sub": sub,
        "rede_id": rede_id,
        "perfil": perfil,
        "escola_id": escola_id,
        "iat": int(utc_now.timestamp()),
        "exp": int((utc_now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError("Token inválido ou expirado.") from exc
    if "sub" not in payload or "rede_id" not in payload or "perfil" not in payload:
        raise TokenError("Token inválido ou expirado.")
    return payload
