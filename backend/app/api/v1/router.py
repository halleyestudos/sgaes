from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers.aluno import router as aluno_router
from app.api.v1.routers.ano_letivo import router as ano_letivo_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.escola import router as escola_router
from app.api.v1.routers.turma import router as turma_router
from app.api.v1.routers.frequencia import router as frequencia_router
from app.api.v1.routers.matricula import router as matricula_router
from app.api.v1.routers.responsavel import router as responsavel_router
from app.api.v1.routers.historico_escolar import router as historico_router
from app.api.v1.routers.geo import router as geo_router
from app.api.v1.routers.lgpd import router as lgpd_router
from app.api.v1.routers.gestao import router as gestao_router
from app.api.v1.routers.modulos_futuros import router as futuros_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(escola_router)
api_router.include_router(ano_letivo_router)
api_router.include_router(turma_router)
api_router.include_router(aluno_router)
api_router.include_router(frequencia_router)
api_router.include_router(matricula_router)
api_router.include_router(responsavel_router)
api_router.include_router(historico_router)
api_router.include_router(geo_router)
api_router.include_router(lgpd_router)
api_router.include_router(gestao_router)
api_router.include_router(futuros_router)
