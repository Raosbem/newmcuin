"""add image_url to parts

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-27
"""
from typing import Union
from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("parts", sa.Column("image_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("parts", "image_url")
