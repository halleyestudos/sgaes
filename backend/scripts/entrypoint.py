from __future__ import annotations

import os
import sys


def main() -> None:
    if os.system(f"{sys.executable} -m alembic upgrade head") != 0:
        raise SystemExit(1)
    if os.environ.get("RUN_SEED", "false").lower() == "true":
        if os.system(f"{sys.executable} -m app.seed") != 0:
            raise SystemExit(1)
    os.execvp(sys.executable, [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()
