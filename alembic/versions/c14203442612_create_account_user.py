"""create account user

Revision ID: c14203442612
Revises:
Create Date: 2025-10-13 20:53:27.996891

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c14203442612"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("first_name", sa.String(), index=True),
        sa.Column("last_name", sa.String(), index=True),
        sa.Column("email", sa.String(), unique=True, index=True),
        sa.Column("hashed_password", sa.String()),
        sa.Column("active", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("users")
