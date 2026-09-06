"""add product media fields

Revision ID: 20260523_0003
Revises: 20260522_0002
Create Date: 2026-05-23 10:15:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260523_0003"
down_revision: str | None = "20260522_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("emoji", sa.String(length=16), nullable=True))
    op.add_column("products", sa.Column("image_path", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "image_path")
    op.drop_column("products", "emoji")
