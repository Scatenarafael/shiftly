"""creates workshifts

Revision ID: f504067f3889
Revises: 416d8be03c11
Create Date: 2025-10-29 17:00:18.913409

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f504067f3889"
down_revision: Union[str, Sequence[str], None] = "416d8be03c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "work_shifts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("work_day_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_days.id", ondelete="CASCADE")),
        sa.Column("weekday", sa.Integer, nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("work_shifts")
