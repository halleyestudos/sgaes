from __future__ import annotations

import os
import sys
import time
from urllib.parse import quote_plus


def ensure_database_url() -> None:
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password:
        print("POSTGRES_PASSWORD não definido.", file=sys.stderr)
        raise SystemExit(1)
    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://postgres:{quote_plus(password)}@db:5432/sga"
    print("DATABASE_URL configurada (senha codificada).")


def run_migrations_with_retry(attempts: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, attempts + 1):
        print(f"Alembic upgrade head (tentativa {attempt}/{attempts})...")
        if os.system(f"{sys.executable} -m alembic upgrade head") == 0:
            print("Migrações aplicadas.")
            return
        time.sleep(delay)
    print("Falha ao aplicar migrações.", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not os.environ.get("SECRET_KEY"):
        print("SECRET_KEY não definido.", file=sys.stderr)
        raise SystemExit(1)

    ensure_database_url()
    run_migrations_with_retry()

    if os.environ.get("RUN_SEED", "false").lower() == "true":
        print("Executando seed...")
        code = os.system(f"{sys.executable} -m app.seed")
        if code != 0:
            # Não derruba a API em produção se o seed falhar (ex.: dados já existentes).
            print("Seed falhou; a API sobe mesmo assim. Ajuste RUN_SEED=false após o primeiro deploy.", file=sys.stderr)

    print("Iniciando uvicorn...")
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    )


if __name__ == "__main__":
    main()
