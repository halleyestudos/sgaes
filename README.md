# SGA-EDU

Sistema de Gestão Acadêmica para redes municipais de ensino.

## Estrutura

- `backend/`: FastAPI + SQLAlchemy 2 assíncrono + Alembic
- `frontend/`: React + TypeScript + Vite
- `docs/`: ADRs e documentação
- `docker-compose.yml`: PostgreSQL local
- `docker-compose.prod.yml`: db + api + web + Caddy

## Como executar no Windows

```powershell
docker compose up -d
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Se o Vite estiver no WSL, use o endereço Network que ele imprimir.

Usuários de demonstração após o seed:

- `gestor@sga.local` / `Gestor@123`
- `secretaria@sga.local` / `Secretaria@123`
- `professor@sga.local` / `Professor@123`

O `rede_id` não vem mais do frontend. Ele entra no JWT no login e as rotas usam só esse valor.

## Produção (Hostinger VPS / Docker)

```powershell
Copy-Item .env.prod.example .env
# edite POSTGRES_PASSWORD, SECRET_KEY e DOMAIN
docker compose -f docker-compose.prod.yml up -d --build
```

O Caddy escuta 80/443, o front fica em `web` e a API em `/api`. O Postgres não é publicado na internet.

## Testes

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

## Estado atual

Funcional:

- login JWT, perfis e tenant derivado do token
- CRUD de escola, ano letivo, turma e aluno
- matrícula, transferência e encerramento
- frequência, consolidação e busca ativa
- compose de produção com Caddy

Ainda não funcional:

- testes automatizados de frontend
- auditoria de leitura de dados pessoais
- recuperação de senha
