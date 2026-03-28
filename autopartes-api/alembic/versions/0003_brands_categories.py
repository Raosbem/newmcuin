"""brands and categories tables, fk in parts, drop brand/category strings

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── brands ────────────────────────────────────────────────────────────────
    op.create_table(
        "brands",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_brands_name", "brands", ["name"], unique=True)

    # ── categories ────────────────────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    # ── add FK columns to parts ───────────────────────────────────────────────
    op.add_column("parts", sa.Column("brand_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("parts", sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_parts_brand_id",    "parts", "brands",     ["brand_id"],    ["id"])
    op.create_foreign_key("fk_parts_category_id", "parts", "categories", ["category_id"], ["id"])

    # ── drop old free-text columns ────────────────────────────────────────────
    op.drop_index("ix_parts_category", table_name="parts")
    op.drop_column("parts", "brand")
    op.drop_column("parts", "category")


def downgrade() -> None:
    op.add_column("parts", sa.Column("brand",    sa.String(100), nullable=True))
    op.add_column("parts", sa.Column("category", sa.String(100), nullable=True))
    op.create_index("ix_parts_category", "parts", ["category"])

    op.drop_constraint("fk_parts_brand_id",    "parts", type_="foreignkey")
    op.drop_constraint("fk_parts_category_id", "parts", type_="foreignkey")
    op.drop_column("parts", "brand_id")
    op.drop_column("parts", "category_id")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_brands_name", table_name="brands")
    op.drop_table("brands")
