"""create cash register sessions

Revision ID: 20260522_0001
Revises:
Create Date: 2026-05-22 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cash_register_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("opening_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expected_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("closing_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("difference_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "uq_cash_register_single_open",
        "cash_register_sessions",
        ["status"],
        unique=True,
        sqlite_where=sa.text("status = 'OPEN'"),
    )


def downgrade() -> None:
    op.drop_index("uq_cash_register_single_open", table_name="cash_register_sessions")
    op.drop_table("cash_register_sessions")
