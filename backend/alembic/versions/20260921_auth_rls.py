"""RLS por tenant e políticas de isolamento.

Revision ID: 20260921_auth_rls
Revises: 20260921_etapa3_frequencia
"""

from __future__ import annotations

from alembic import op

revision = "20260921_auth_rls"
down_revision = "20260921_etapa3_frequencia"
branch_labels = None
depends_on = None

TABLES = ("escola", "ano_letivo", "turma", "aluno", "matricula", "frequencia", "alerta_frequencia")


def upgrade() -> None:
    for table in TABLES:
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
    for table in TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON sga.{table}")
        op.execute(f"ALTER TABLE sga.{table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE sga.{table} DISABLE ROW LEVEL SECURITY")
