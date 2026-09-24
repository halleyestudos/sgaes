"""Expansão Censo/geo/LGPD/ambiente.

Revision ID: 20260923_expansao_produto
Revises: 20260921_auth_rls
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260923_expansao_produto"
down_revision = "20260921_auth_rls"
branch_labels = None
depends_on = None

NEW_TABLES = ("responsavel", "historico_escolar", "consentimento_lgpd")


def upgrade() -> None:
    op.add_column("escola", sa.Column("dependencia_administrativa", sa.String(40), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("telefone", sa.String(30), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("email", sa.String(255), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("endereco", sa.String(255), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("bairro", sa.String(120), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("cidade", sa.String(120), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("uf", sa.String(2), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("cep", sa.String(12), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("latitude", sa.Float(), nullable=True), schema="sga")
    op.add_column("escola", sa.Column("longitude", sa.Float(), nullable=True), schema="sga")

    op.add_column("turma", sa.Column("professor_id", sa.Integer(), sa.ForeignKey("sga.usuario.id"), nullable=True), schema="sga")
    op.add_column("turma", sa.Column("oferece_merenda", sa.Boolean(), nullable=False, server_default=sa.text("true")), schema="sga")
    op.add_column("turma", sa.Column("apoio_pedagogico", sa.Boolean(), nullable=False, server_default=sa.text("false")), schema="sga")

    for col, coltype in [
        ("cor_raca", sa.String(40)),
        ("naturalidade_cidade", sa.String(120)),
        ("naturalidade_uf", sa.String(2)),
        ("telefone", sa.String(30)),
        ("email", sa.String(255)),
        ("nome_mae", sa.String(255)),
        ("nome_pai", sa.String(255)),
        ("endereco", sa.String(255)),
        ("numero", sa.String(20)),
        ("complemento", sa.String(120)),
        ("bairro", sa.String(120)),
        ("cidade", sa.String(120)),
        ("uf", sa.String(2)),
        ("cep", sa.String(12)),
        ("latitude", sa.Float()),
        ("longitude", sa.Float()),
        ("modal_transporte", sa.String(40)),
        ("distancia_metros", sa.Numeric(12, 2)),
        ("tempo_deslocamento_min", sa.Integer()),
        ("metodo_distancia", sa.String(40)),
        ("acesso_internet", sa.Boolean()),
        ("acesso_materiais", sa.Boolean()),
        ("necessidades_especiais", sa.Text()),
        ("dados_anonimizados", sa.Boolean()),
    ]:
        kwargs = {"nullable": True}
        if col == "dados_anonimizados":
            op.add_column("aluno", sa.Column(col, coltype, nullable=False, server_default=sa.text("false")), schema="sga")
        else:
            op.add_column("aluno", sa.Column(col, coltype, **kwargs), schema="sga")

    op.create_table(
        "responsavel",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), sa.ForeignKey("sga.rede.id"), nullable=False),
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("sga.aluno.id"), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("parentesco", sa.String(60), nullable=True),
        sa.Column("telefone", sa.String(30), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("cpf", sa.String(14), nullable=True),
        sa.Column("principal", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="sga",
    )
    op.create_index("ix_responsavel_rede_id", "responsavel", ["rede_id"], schema="sga")
    op.create_index("ix_responsavel_aluno_id", "responsavel", ["aluno_id"], schema="sga")

    op.create_table(
        "historico_escolar",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), sa.ForeignKey("sga.rede.id"), nullable=False),
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("sga.aluno.id"), nullable=False),
        sa.Column("nome_escola", sa.String(255), nullable=False),
        sa.Column("codigo_inep", sa.String(20), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=True),
        sa.Column("serie", sa.String(40), nullable=True),
        sa.Column("ultima_escola", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("observacao", sa.Text(), nullable=True),
        schema="sga",
    )
    op.create_index("ix_historico_escolar_rede_id", "historico_escolar", ["rede_id"], schema="sga")
    op.create_index("ix_historico_escolar_aluno_id", "historico_escolar", ["aluno_id"], schema="sga")

    op.create_table(
        "consentimento_lgpd",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rede_id", sa.Integer(), sa.ForeignKey("sga.rede.id"), nullable=False),
        sa.Column("aluno_id", sa.Integer(), sa.ForeignKey("sga.aluno.id"), nullable=False),
        sa.Column("responsavel_id", sa.Integer(), sa.ForeignKey("sga.responsavel.id"), nullable=True),
        sa.Column("tipo", sa.String(80), nullable=False, server_default="tratamento_dados"),
        sa.Column("finalidade", sa.Text(), nullable=True),
        sa.Column("concedido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("data_registro", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("registrado_por", sa.String(255), nullable=True),
        schema="sga",
    )
    op.create_index("ix_consentimento_lgpd_rede_id", "consentimento_lgpd", ["rede_id"], schema="sga")
    op.create_index("ix_consentimento_lgpd_aluno_id", "consentimento_lgpd", ["aluno_id"], schema="sga")

    for table in NEW_TABLES:
        op.execute(f"ALTER TABLE sga.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE sga.{table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON sga.{table}")
        op.execute(
            f"""
            CREATE POLICY tenant_isolation ON sga.{table}
            USING (rede_id = NULLIF(current_setting('sga.rede_id', true), '')::int)
            WITH CHECK (rede_id = NULLIF(current_setting('sga.rede_id', true), '')::int)
            """
        )


def downgrade() -> None:
    for table in NEW_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON sga.{table}")
        op.drop_table(table, schema="sga")

    for col in [
        "cor_raca", "naturalidade_cidade", "naturalidade_uf", "telefone", "email", "nome_mae", "nome_pai",
        "endereco", "numero", "complemento", "bairro", "cidade", "uf", "cep", "latitude", "longitude",
        "modal_transporte", "distancia_metros", "tempo_deslocamento_min", "metodo_distancia",
        "acesso_internet", "acesso_materiais", "necessidades_especiais", "dados_anonimizados",
    ]:
        op.drop_column("aluno", col, schema="sga")

    op.drop_column("turma", "apoio_pedagogico", schema="sga")
    op.drop_column("turma", "oferece_merenda", schema="sga")
    op.drop_column("turma", "professor_id", schema="sga")

    for col in [
        "dependencia_administrativa", "telefone", "email", "endereco", "bairro", "cidade", "uf", "cep", "latitude", "longitude",
    ]:
        op.drop_column("escola", col, schema="sga")
