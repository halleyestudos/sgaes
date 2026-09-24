"""Etapa 3: matriculas, frequencia e alertas.

Revision ID: 20260921_etapa3_frequencia
Revises: 20260921_initial_schema
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260921_etapa3_frequencia"
down_revision = "20260921_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matricula",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("turma_id", sa.Integer(), nullable=False),
        sa.Column("ano_letivo_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="ATIVA"),
        sa.Column("data_matricula", sa.Date(), nullable=False),
        sa.Column("data_encerramento", sa.Date(), nullable=True),
        sa.Column("motivo_encerramento", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"]),
        sa.ForeignKeyConstraint(["aluno_id"], ["sga.aluno.id"]),
        sa.ForeignKeyConstraint(["turma_id"], ["sga.turma.id"]),
        sa.ForeignKeyConstraint(["ano_letivo_id"], ["sga.ano_letivo.id"]),
        schema="sga",
    )
    op.create_index("idx_matricula_aluno_ano_ativa", "matricula", ["aluno_id", "ano_letivo_id"], unique=True, schema="sga", postgresql_where=sa.text("status = 'ATIVA'"))
    op.create_index("idx_matricula_turma_status", "matricula", ["turma_id", "status"], schema="sga")

    op.create_table(
        "frequencia",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("turma_id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("presente", sa.Boolean(), nullable=False),
        sa.Column("observacao", sa.String(255), nullable=True),
        sa.Column("registrada_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"]),
        sa.ForeignKeyConstraint(["turma_id"], ["sga.turma.id"]),
        sa.ForeignKeyConstraint(["aluno_id"], ["sga.aluno.id"]),
        schema="sga",
    )
    op.create_index("idx_frequencia_idempotencia", "frequencia", ["turma_id", "aluno_id", "data", "ordem"], unique=True, schema="sga")

    op.create_table(
        "alerta_frequencia",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("ano_letivo_id", sa.Integer(), nullable=False),
        sa.Column("nivel", sa.String(30), nullable=False),
        sa.Column("percentual", sa.Numeric(5, 2), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolvido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"]),
        sa.ForeignKeyConstraint(["aluno_id"], ["sga.aluno.id"]),
        sa.ForeignKeyConstraint(["ano_letivo_id"], ["sga.ano_letivo.id"]),
        schema="sga",
    )
    op.create_index("idx_alerta_frequencia_aluno_ano", "alerta_frequencia", ["aluno_id", "ano_letivo_id"], unique=True, schema="sga")


def downgrade() -> None:
    op.drop_index("idx_alerta_frequencia_aluno_ano", table_name="alerta_frequencia", schema="sga")
    op.drop_table("alerta_frequencia", schema="sga")
    op.drop_index("idx_frequencia_idempotencia", table_name="frequencia", schema="sga")
    op.drop_table("frequencia", schema="sga")
    op.drop_index("idx_matricula_turma_status", table_name="matricula", schema="sga")
    op.drop_index("idx_matricula_aluno_ano_ativa", table_name="matricula", schema="sga")
    op.drop_table("matricula", schema="sga")
