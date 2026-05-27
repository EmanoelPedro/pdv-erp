"""create expenses table

Revision ID: 20260523_0004
Revises: 20260523_0003
Create Date: 2026-05-23 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260523_0004"
down_revision: str | None = "20260523_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "expenses",
        sa.Column("id", sa.String(length=36),
                  primary_key=True, nullable=False),
        sa.Column(
            "cash_register_session_id",
            sa.String(length=36),
            sa.ForeignKey("cash_register_sessions.id"),
            nullable=True,
        ),
        sa.Column("description", sa.String(length=160), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "created_by_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("expense_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_expenses_cash_register_session_id", "expenses", [
                    "cash_register_session_id"], unique=False)
    op.create_index("ix_expenses_description", "expenses",
                    ["description"], unique=False)
    op.create_index("ix_expenses_category", "expenses",
                    ["category"], unique=False)
    op.create_index("ix_expenses_created_by_user_id", "expenses", [
                    "created_by_user_id"], unique=False)
    op.create_index("ix_expenses_expense_date", "expenses",
                    ["expense_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_expenses_expense_date", table_name="expenses")
    op.drop_index("ix_expenses_created_by_user_id", table_name="expenses")
    op.drop_index("ix_expenses_category", table_name="expenses")
    op.drop_index("ix_expenses_description", table_name="expenses")
    op.drop_index("ix_expenses_cash_register_session_id",
                  table_name="expenses")
    op.drop_table("expenses")
