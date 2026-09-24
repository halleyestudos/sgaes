from sqlalchemy.orm import configure_mappers

from app.models.rede import Rede
from app.models.escola import Escola
from app.models.ano_letivo import AnoLetivo
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.frequencia import Frequencia
from app.models.alerta_frequencia import AlertaFrequencia
from app.models.usuario import Usuario
from app.models.responsavel import Responsavel
from app.models.historico_escolar import HistoricoEscolar
from app.models.consentimento_lgpd import ConsentimentoLgpd

configure_mappers()

__all__ = [
    "Rede",
    "Escola",
    "AnoLetivo",
    "Turma",
    "Aluno",
    "Matricula",
    "Frequencia",
    "AlertaFrequencia",
    "Usuario",
    "Responsavel",
    "HistoricoEscolar",
    "ConsentimentoLgpd",
]
