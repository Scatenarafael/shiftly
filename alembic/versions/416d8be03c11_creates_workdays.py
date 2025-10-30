"""creates workdays

Revision ID: 416d8be03c11
Revises: 3ab042394f8d
Create Date: 2025-10-29 17:00:02.452213

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "416d8be03c11"
down_revision: Union[str, Sequence[str], None] = "3ab042394f8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "work_days",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE")),
        sa.Column("weekday", sa.Integer, nullable=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_holiday", sa.Boolean, nullable=False, default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("work_days")
