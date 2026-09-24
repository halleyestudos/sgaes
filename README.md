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

## Produção no Dokploy (Hostinger VPS) — recomendado

Arquivo: `docker-compose.dokploy.yml` (sem Caddy; o Traefik do Dokploy cuida de HTTPS).

1. Em https://admin.sgaes.tech/ crie um **Project** → **Compose**.
2. Source: GitHub `halleyestudos/sgaes`, branch `main`.
3. Compose path: `docker-compose.dokploy.yml`.
4. Aba **Environment** (valores reais, não os de exemplo):

```env
POSTGRES_PASSWORD=...senha-forte...
SECRET_KEY=...chave-longa-aleatoria...
CORS_ORIGINS=https://sgaes.tech,https://www.sgaes.tech
JWT_EXPIRE_MINUTES=480
RUN_SEED=true
```

5. Aba **Domains**:
   - Host: `sgaes.tech` (e opcionalmente `www.sgaes.tech`)
   - Service: `web`
   - Port: `80`
   - HTTPS / Let's Encrypt: ligado
6. **Deploy**. Depois do primeiro seed bem-sucedido, mude `RUN_SEED=false` e redeploy.
7. Login demo: `gestor@sga.local` / `Gestor@123`

O nginx do `web` encaminha `/api`, `/health` e `/docs` para o serviço `api`.

DNS: `A` de `sgaes.tech` (e `www`) → IP da VPS. `admin.sgaes.tech` já aponta para o Dokploy.

## Produção alternativa (Compose + Caddy na própria VPS)

Use se **não** estiver usando Dokploy/Traefik (conflita nas portas 80/443):

```powershell
Copy-Item .env.prod.example .env
# edite POSTGRES_PASSWORD, SECRET_KEY e DOMAIN=sgaes.tech
docker compose -f docker-compose.prod.yml up -d --build
```

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
- cadastro ampliado (Censo, responsáveis, histórico escolar)
- geo/deslocamento, painel por bairro, LGPD básica
- compose de produção com Caddy

Ainda não funcional:

- testes automatizados de frontend
- auditoria de leitura de dados pessoais
- recuperação de senha
