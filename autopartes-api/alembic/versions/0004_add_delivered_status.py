"""add delivered to orderstatus enum

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-27
"""
from typing import Union
from alembic import op


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'delivered'")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de un enum directamente;
    # el downgrade requeriría recrear el tipo, lo cual es destructivo.
    pass
