from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aluno import Aluno
from app.models.ano_letivo import AnoLetivo
from app.models.escola import Escola
from app.models.turma import Turma


class CadastroService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def criar_escola(self, *, nome: str, codigo_inep: str | None, rede_id: int) -> Escola:
        escola = Escola(rede_id=rede_id, nome=nome, codigo_inep=codigo_inep, ativo=True)
        self.session.add(escola)
        await self.session.commit()
        await self.session.refresh(escola)
        return escola

    async def criar_ano_letivo(self, *, nome: str, rede_id: int) -> AnoLetivo:
        ano = AnoLetivo(rede_id=rede_id, nome=nome, ativo=True)
        self.session.add(ano)
        await self.session.commit()
        await self.session.refresh(ano)
        return ano

    async def criar_turma(self, *, nome: str, escola_id: int, ano_letivo_id: int, rede_id: int, serie: str | None = None, turno: str | None = None) -> Turma:
        turma = Turma(rede_id=rede_id, escola_id=escola_id, ano_letivo_id=ano_letivo_id, nome=nome, serie=serie, turno=turno, ativa=True)
        self.session.add(turma)
        await self.session.commit()
        await self.session.refresh(turma)
        return turma

    async def criar_aluno(self, *, nome: str, rede_id: int, nome_social: str | None = None, data_nascimento=None, sexo: str | None = None) -> Aluno:
        aluno = Aluno(rede_id=rede_id, nome=nome, nome_social=nome_social, data_nascimento=data_nascimento, sexo=sexo, ativo=True)
        self.session.add(aluno)
        await self.session.commit()
        await self.session.refresh(aluno)
        return aluno
