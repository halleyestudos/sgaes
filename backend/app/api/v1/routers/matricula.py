from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PERFIS_CADASTRO, get_current_user, get_owned, require_perfil
from app.db.session import get_db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.schemas.matricula import AlunoTurmaRead, EncerramentoCreate, MatriculaCreate, MatriculaRead, TransferenciaCreate
from app.services.matricula_service import MatriculaService

router = APIRouter(prefix="/matriculas", tags=["matriculas"])


@router.post("", response_model=MatriculaRead, status_code=status.HTTP_201_CREATED, summary="Matricular aluno", description="Cria uma matrícula ativa na rede do token.", responses={201: {"description": "Matrícula criada."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}, 409: {"description": "Aluno já matriculado no ano letivo."}})
async def criar_matricula(payload: MatriculaCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Matricula:
    dados = payload.model_dump()
    dados["rede_id"] = usuario.rede_id
    return await MatriculaService(db).criar(**dados)


@router.get("/turma/{turma_id}/alunos", response_model=list[AlunoTurmaRead], summary="Listar alunos da turma", description="Lista os alunos com matrícula ativa na turma da rede autenticada.", responses={200: {"description": "Alunos listados."}, 401: {"description": "Token inválido ou ausente."}, 404: {"description": "Turma não encontrada."}})
async def listar_alunos_da_turma(turma_id: int, usuario: Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[AlunoTurmaRead]:
    await get_owned(db, Turma, turma_id, usuario, "Turma não encontrada.")
    rows = (
        await db.execute(
            select(Aluno.id, Aluno.nome, Matricula.id, Matricula.status)
            .join(Matricula, Matricula.aluno_id == Aluno.id)
            .where(Matricula.turma_id == turma_id, Matricula.status == "ATIVA", Matricula.rede_id == usuario.rede_id)
            .order_by(Aluno.nome)
        )
    ).all()
    return [AlunoTurmaRead(aluno_id=aluno_id, nome=nome, matricula_id=matricula_id, status=status_) for aluno_id, nome, matricula_id, status_ in rows]


@router.put("/{matricula_id}/transferir", response_model=MatriculaRead, summary="Transferir aluno", description="Encerra a matrícula atual e cria outra na nova turma do mesmo ano letivo.", responses={200: {"description": "Aluno transferido."}, 400: {"description": "Transferência inválida."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def transferir_matricula(matricula_id: int, payload: TransferenciaCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Matricula:
    await get_owned(db, Matricula, matricula_id, usuario, "Matrícula não encontrada.")
    return await MatriculaService(db).transferir(matricula_id, payload.nova_turma_id, payload.motivo)


@router.put("/{matricula_id}/encerrar", response_model=MatriculaRead, summary="Encerrar matrícula", description="Encerra uma matrícula ativa com motivo obrigatório.", responses={200: {"description": "Matrícula encerrada."}, 400: {"description": "Matrícula já encerrada."}, 401: {"description": "Token inválido ou ausente."}, 403: {"description": "Perfil sem permissão."}})
async def encerrar_matricula(matricula_id: int, payload: EncerramentoCreate, usuario: Usuario = Depends(require_perfil(*PERFIS_CADASTRO)), db: AsyncSession = Depends(get_db)) -> Matricula:
    await get_owned(db, Matricula, matricula_id, usuario, "Matrícula não encontrada.")
    return await MatriculaService(db).encerrar(matricula_id, payload.motivo)
