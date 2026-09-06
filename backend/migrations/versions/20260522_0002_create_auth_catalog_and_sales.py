"""create auth catalog and sales tables

Revision ID: 20260522_0002
Revises: 20260522_0001
Create Date: 2026-05-22 00:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_0002"
down_revision: str | None = "20260522_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("username", sa.String(length=60), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("pin_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_sessions_token_hash", "user_sessions", ["token_hash"], unique=True)
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)
    op.create_index("ix_products_name", "products", ["name"], unique=False)

    op.create_table(
        "sales",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "cash_register_session_id",
            sa.String(length=36),
            sa.ForeignKey("cash_register_sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "seller_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("cash_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("pix_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("debit_card_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("credit_card_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_sales_cash_register_session_id",
        "sales",
        ["cash_register_session_id"],
        unique=False,
    )
    op.create_index("ix_sales_seller_user_id", "sales", ["seller_user_id"], unique=False)

    op.create_table(
        "sale_items",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sale_id", sa.String(length=36), sa.ForeignKey("sales.id"), nullable=False),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name", sa.String(length=120), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sale_items_sale_id", table_name="sale_items")
    op.drop_table("sale_items")
    op.drop_index("ix_sales_seller_user_id", table_name="sales")
    op.drop_index("ix_sales_cash_register_session_id", table_name="sales")
    op.drop_table("sales")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_index("ix_user_sessions_token_hash", table_name="user_sessions")
    op.drop_table("user_sessions")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
