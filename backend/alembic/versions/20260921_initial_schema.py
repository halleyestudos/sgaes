"""initial schema

Revision ID: 20260921_initial_schema
Revises: 
Create Date: 2026-09-21 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260921_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS sga")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "rede",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_rede_id"), "rede", ["id"], unique=False, schema="sga")
    op.create_index("idx_rede_nome", "rede", ["nome"], unique=True, schema="sga")

    op.create_table(
        "escola",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("codigo_inep", sa.String(length=20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"], name="fk_escola_rede"),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_escola_id"), "escola", ["id"], unique=False, schema="sga")
    op.create_index(op.f("ix_sga_escola_rede_id"), "escola", ["rede_id"], unique=False, schema="sga")

    op.create_table(
        "ano_letivo",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"], name="fk_ano_letivo_rede"),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_ano_letivo_id"), "ano_letivo", ["id"], unique=False, schema="sga")
    op.create_index(op.f("ix_sga_ano_letivo_rede_id"), "ano_letivo", ["rede_id"], unique=False, schema="sga")
    op.create_index("idx_ano_letivo_rede_nome", "ano_letivo", ["rede_id", "nome"], unique=True, schema="sga")

    op.create_table(
        "turma",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("escola_id", sa.Integer(), nullable=False),
        sa.Column("ano_letivo_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("serie", sa.String(length=20), nullable=True),
        sa.Column("turno", sa.String(length=20), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"], name="fk_turma_rede"),
        sa.ForeignKeyConstraint(["escola_id"], ["sga.escola.id"], name="fk_turma_escola"),
        sa.ForeignKeyConstraint(["ano_letivo_id"], ["sga.ano_letivo.id"], name="fk_turma_ano_letivo"),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_turma_id"), "turma", ["id"], unique=False, schema="sga")
    op.create_index(op.f("ix_sga_turma_rede_id"), "turma", ["rede_id"], unique=False, schema="sga")

    op.create_table(
        "aluno",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("nome_social", sa.String(length=255), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"], name="fk_aluno_rede"),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_aluno_id"), "aluno", ["id"], unique=False, schema="sga")
    op.create_index(op.f("ix_sga_aluno_rede_id"), "aluno", ["rede_id"], unique=False, schema="sga")

    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("rede_id", sa.Integer(), nullable=False),
        sa.Column("escola_id", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("perfil", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["rede_id"], ["sga.rede.id"], name="fk_usuario_rede"),
        sa.ForeignKeyConstraint(["escola_id"], ["sga.escola.id"], name="fk_usuario_escola"),
        schema="sga",
    )
    op.create_index(op.f("ix_sga_usuario_id"), "usuario", ["id"], unique=False, schema="sga")
    op.create_index(op.f("ix_sga_usuario_rede_id"), "usuario", ["rede_id"], unique=False, schema="sga")
    op.create_index("ix_usuario_email_unique", "usuario", ["email"], unique=True, schema="sga")


def downgrade() -> None:
    op.drop_index("ix_usuario_email_unique", table_name="usuario", schema="sga")
    op.drop_index(op.f("ix_sga_usuario_rede_id"), table_name="usuario", schema="sga")
    op.drop_index(op.f("ix_sga_usuario_id"), table_name="usuario", schema="sga")
    op.drop_table("usuario", schema="sga")

    op.drop_index(op.f("ix_sga_aluno_rede_id"), table_name="aluno", schema="sga")
    op.drop_index(op.f("ix_sga_aluno_id"), table_name="aluno", schema="sga")
    op.drop_table("aluno", schema="sga")

    op.drop_index(op.f("ix_sga_turma_rede_id"), table_name="turma", schema="sga")
    op.drop_index(op.f("ix_sga_turma_id"), table_name="turma", schema="sga")
    op.drop_table("turma", schema="sga")

    op.drop_index("idx_ano_letivo_rede_nome", table_name="ano_letivo", schema="sga")
    op.drop_index(op.f("ix_sga_ano_letivo_rede_id"), table_name="ano_letivo", schema="sga")
    op.drop_index(op.f("ix_sga_ano_letivo_id"), table_name="ano_letivo", schema="sga")
    op.drop_table("ano_letivo", schema="sga")

    op.drop_index(op.f("ix_sga_escola_rede_id"), table_name="escola", schema="sga")
    op.drop_index(op.f("ix_sga_escola_id"), table_name="escola", schema="sga")
    op.drop_table("escola", schema="sga")

    op.drop_index("idx_rede_nome", table_name="rede", schema="sga")
    op.drop_index(op.f("ix_sga_rede_id"), table_name="rede", schema="sga")
    op.drop_table("rede", schema="sga")
