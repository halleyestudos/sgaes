from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import IntegrityError

import app.models  # noqa: F401
from app.api.v1.router import api_router
from app.core.config import get_settings

app = FastAPI(title="SGA-EDU", version="0.1.0", description="Sistema de Gestão Acadêmica para redes municipais de ensino.")
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in _settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


def _mensagem_integridade(exc: IntegrityError) -> str:
    detalhe = str(getattr(exc, "orig", exc))
    if "idx_ano_letivo_rede_nome" in detalhe:
        return "Já existe um ano letivo com esse nome nesta rede."
    if "idx_matricula_aluno_ano_ativa" in detalhe:
        return "O aluno já possui matrícula ativa neste ano letivo."
    if "idx_frequencia_idempotencia" in detalhe:
        return "Esta chamada já foi registrada para o aluno nesta data."
    if "fk_" in detalhe or "ForeignKeyViolation" in detalhe:
        return "Não foi possível gravar: há um vínculo inválido com escola, turma, aluno ou rede."
    return "Não foi possível gravar: registro duplicado ou vínculo inválido."


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": _mensagem_integridade(exc)})


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <html>
      <head>
        <title>SGA-EDU MVP</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          body { font-family: Arial, sans-serif; background: #f3f7fb; color: #122033; margin: 0; padding: 40px; }
          .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 18px; padding: 32px; box-shadow: 0 12px 30px rgba(18, 32, 51, 0.08); }
          h1 { color: #0b5ed7; }
          .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; }
          .card { background: #edf4ff; border-radius: 12px; padding: 18px; }
          code { background: #eef2f7; padding: 3px 6px; border-radius: 6px; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>SGA-EDU MVP</h1>
          <p>Etapa 1 concluída e Etapa 2 ativa: cadastro de escola, ano letivo, turma e aluno.</p>
          <div class="cards">
            <div class="card"><strong>API:</strong><br /><code>/api/v1/escolas</code></div>
            <div class="card"><strong>API:</strong><br /><code>/api/v1/anos-letivos</code></div>
            <div class="card"><strong>API:</strong><br /><code>/api/v1/turmas</code></div>
            <div class="card"><strong>API:</strong><br /><code>/api/v1/alunos</code></div>
          </div>
          <p>Documentação interativa em <code>/docs</code>. Endpoints ativos: <code>/health</code>, <code>/</code> e rotas da API v1.</p>
        </div>
      </body>
    </html>
    """


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "app": "sga-edu"}
