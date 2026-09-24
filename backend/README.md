# Backend SGA-EDU

## Requisitos

- Python 3.12
- PostgreSQL 16
- Docker Compose (opcional para infra)

## Ambiente local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cp .env.example .env
```

Em PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
```

## Rodar testes

```bash
cd backend
python -m pytest -q
```

## Rodar aplicação

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Alembic

```bash
cd backend
alembic upgrade head
```
