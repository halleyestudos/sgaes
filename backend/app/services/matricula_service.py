from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aluno import Aluno
from app.models.ano_letivo import AnoLetivo
from app.models.matricula import Matricula
from app.models.turma import Turma


class MatriculaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def criar(self, *, aluno_id: int, turma_id: int, ano_letivo_id: int, rede_id: int, data_matricula: date | None) -> Matricula:
        aluno = await self.session.get(Aluno, aluno_id)
        turma = await self.session.get(Turma, turma_id)
        ano = await self.session.get(AnoLetivo, ano_letivo_id)
        if aluno is None or turma is None or ano is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno, turma ou ano letivo não encontrado.")
        if aluno.rede_id != rede_id or turma.rede_id != rede_id or ano.rede_id != rede_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno, turma ou ano letivo não encontrado.")
        if turma.ano_letivo_id != ano_letivo_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A turma não pertence ao ano letivo informado.")
        ativa = await self.session.scalar(select(Matricula).where(Matricula.aluno_id == aluno_id, Matricula.ano_letivo_id == ano_letivo_id, Matricula.status == "ATIVA"))
        if ativa is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O aluno já possui matrícula ativa neste ano letivo.")
        matricula = Matricula(rede_id=rede_id, aluno_id=aluno_id, turma_id=turma_id, ano_letivo_id=ano_letivo_id, data_matricula=data_matricula or date.today(), status="ATIVA")
        self.session.add(matricula)
        await self.session.commit()
        await self.session.refresh(matricula)
        return matricula

    async def transferir(self, matricula_id: int, nova_turma_id: int, motivo: str | None) -> Matricula:
        atual = await self.session.get(Matricula, matricula_id)
        nova_turma = await self.session.get(Turma, nova_turma_id)
        if atual is None or nova_turma is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula ou nova turma não encontrada.")
        if nova_turma.rede_id != atual.rede_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula ou nova turma não encontrada.")
        if atual.status != "ATIVA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Somente matrículas ativas podem ser transferidas.")
        if nova_turma.ano_letivo_id != atual.ano_letivo_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A nova turma deve pertencer ao mesmo ano letivo.")
        atual.status = "TRANSFERIDA"
        atual.data_encerramento = date.today()
        atual.motivo_encerramento = motivo or "Transferência de turma"
        nova = Matricula(rede_id=atual.rede_id, aluno_id=atual.aluno_id, turma_id=nova_turma_id, ano_letivo_id=atual.ano_letivo_id, status="ATIVA", data_matricula=date.today())
        self.session.add(nova)
        await self.session.commit()
        await self.session.refresh(nova)
        return nova

    async def encerrar(self, matricula_id: int, motivo: str) -> Matricula:
        matricula = await self.session.get(Matricula, matricula_id)
        if matricula is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada.")
        if matricula.status != "ATIVA":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A matrícula já está encerrada.")
        matricula.status = "ENCERRADA"
        matricula.data_encerramento = date.today()
        matricula.motivo_encerramento = motivo
        await self.session.commit()
        await self.session.refresh(matricula)
        return matricula
