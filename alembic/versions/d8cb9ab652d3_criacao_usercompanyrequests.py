"""criacao_UserCompanyRequests

Revision ID: d8cb9ab652d3
Revises: 18b3ae4a4e1f
Create Date: 2026-02-24 23:53:08.827372

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8cb9ab652d3"
down_revision: Union[str, Sequence[str], None] = "18b3ae4a4e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_company_request_status = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        name="user_company_request_status",
    )
    user_company_request_status.create(op.get_bind(), checkfirst=True)

    user_company_request_status_enum = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        name="user_company_request_status",
        create_type=False,
    )

    op.create_table(
        "user_company_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE")),
        sa.Column("status", user_company_request_status_enum, nullable=False, default="pending"),
        sa.Column("accepted", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_company_requests")

    user_company_request_status = postgresql.ENUM(
        "pending",
        "approved",
        "rejected",
        name="user_company_request_status",
    )
    user_company_request_status.drop(op.get_bind(), checkfirst=True)
