from __future__ import annotations

from contextvars import ContextVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_TENANT_CONTEXT: ContextVar[int | None] = ContextVar("tenant_context", default=None)


async def set_tenant(rede_id: int, db: AsyncSession | None = None) -> None:
    _TENANT_CONTEXT.set(rede_id)
    if db is not None:
        await db.execute(text("SELECT set_config('sga.rede_id', :rede_id, true)"), {"rede_id": str(rede_id)})


def get_tenant_id() -> int | None:
    return _TENANT_CONTEXT.get()


async def ensure_tenant_context(rede_id: int, db: AsyncSession | None = None) -> None:
    await set_tenant(rede_id, db=db)
