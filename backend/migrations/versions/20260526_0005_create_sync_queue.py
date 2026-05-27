"""create sync queue table

Revision ID: 20260526_0005
Revises: 20260523_0004
Create Date: 2026-05-26 14:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260526_0005"
down_revision: str | None = "20260523_0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sync_queue",
        sa.Column("id", sa.String(length=36),
                  primary_key=True, nullable=False),
        sa.Column("entity_type", sa.String(length=60), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("sync_status", sa.String(length=20), nullable=False),
        sa.Column("retry_count", sa.Integer(),
                  nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sync_queue_sync_status", "sync_queue",
                    ["sync_status"], unique=False)
    op.create_index("ix_sync_queue_created_at", "sync_queue",
                    ["created_at"], unique=False)
    op.create_index("ix_sync_queue_entity_type", "sync_queue",
                    ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sync_queue_entity_type", table_name="sync_queue")
    op.drop_index("ix_sync_queue_created_at", table_name="sync_queue")
    op.drop_index("ix_sync_queue_sync_status", table_name="sync_queue")
    op.drop_table("sync_queue")
