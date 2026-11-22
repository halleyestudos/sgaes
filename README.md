# SGA-EDU

Sistema de Gestão Acadêmica para redes municipais de ensino.

## Estrutura

- `backend/`: FastAPI + SQLAlchemy 2 assíncrono + Alembic
- `frontend/`: React + TypeScript + Vite
- `docs/`: ADRs e documentação
- `docker-compose.yml`: PostgreSQL local
- `docker-compose.prod.yml`: db + api + web + Caddy

## Desenvolvimento local no Windows

```powershell
docker compose up -d
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Se o Vite estiver no WSL, use o endereço Network que ele imprimir.

O seed cria contas de demonstração para desenvolvimento local.

O `rede_id` não vem mais do frontend. Ele entra no JWT no login e as rotas usam só esse valor.

## Produção no Dokploy (Hostinger VPS) — recomendado

Arquivo: `docker-compose.dokploy.yml` (sem Caddy; o Traefik do Dokploy cuida de HTTPS).

1. Em https://admin.sgaes.tech/ crie um **Project** → **Compose**.
2. Source: GitHub `halleyestudos/sgaes`, branch `main`.
3. Compose path: `docker-compose.dokploy.yml`.
4. Na aba **Environment**, configure uma senha exclusiva para o PostgreSQL e uma chave de assinatura JWT aleatória, longa e exclusiva. Use os identificadores abaixo e preencha os valores diretamente no Dokploy.

```env
POSTGRES_PASSWORD=
SECRET_KEY=
CORS_ORIGINS=https://sgaes.tech,https://www.sgaes.tech
JWT_EXPIRE_MINUTES=480
RUN_SEED=false
```

5. Aba **Domains**:
   - Host: `sgaes.tech` (e opcionalmente `www.sgaes.tech`)
   - Service: `web`
   - Port: `80`
   - HTTPS / Let's Encrypt: ligado
6. Mantenha `RUN_SEED=false` em todos os deploys de produção. Use contas individuais provisionadas para o ambiente.

O nginx do `web` encaminha `/api`, `/health` e `/docs` para o serviço `api`.

DNS: `A` de `sgaes.tech` (e `www`) → IP da VPS. `admin.sgaes.tech` já aponta para o Dokploy.

## Produção alternativa (Compose + Caddy na própria VPS)

Use se **não** estiver usando Dokploy/Traefik (conflita nas portas 80/443):

```powershell
Copy-Item .env.prod.example .env
# Preencha POSTGRES_PASSWORD e SECRET_KEY com valores exclusivos e mantenha RUN_SEED=false.
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
