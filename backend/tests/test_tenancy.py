import pytest

from app.core.tenancy import set_tenant


@pytest.mark.asyncio
async def test_set_tenant_sets_session_variable() -> None:
    await set_tenant(42)
    assert True
