"""add superadmin role

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-27

"""
from alembic import op

revision: str = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ALTER TYPE ADD VALUE IF NOT EXISTS es idempotente en PostgreSQL 12+
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'superadmin';")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de un ENUM sin recrear el tipo.
    # El downgrade requeriría pasos manuales; se deja como no-op intencional.
    pass
