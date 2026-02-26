"""create account user_company_roles

Revision ID: 0fcc52a27d72
Revises: 2c6a9cfac413
Create Date: 2025-10-13 21:00:31.475375

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0fcc52a27d72"
down_revision: Union[str, Sequence[str], None] = "2c6a9cfac413"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "user_company_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE")),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, default=None),
        sa.Column("is_owner", sa.Boolean(), default=False),
    )


def downgrade():
    op.drop_table("user_company_roles")
