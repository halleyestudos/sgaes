from app.schemas.aluno import AlunoCreate, AlunoRead, AlunoUpdate
from app.schemas.ano_letivo import AnoLetivoCreate, AnoLetivoRead, AnoLetivoUpdate
from app.schemas.escola import EscolaCreate, EscolaRead, EscolaUpdate
from app.schemas.turma import TurmaCreate, TurmaRead, TurmaUpdate
from app.schemas.matricula import MatriculaCreate, MatriculaRead

__all__ = [
    "EscolaCreate",
    "EscolaRead",
    "EscolaUpdate",
    "AnoLetivoCreate",
    "AnoLetivoRead",
    "AnoLetivoUpdate",
    "TurmaCreate",
    "TurmaRead",
    "TurmaUpdate",
    "AlunoCreate",
    "AlunoRead",
    "AlunoUpdate",
    "MatriculaCreate",
    "MatriculaRead",
]
