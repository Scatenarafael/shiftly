"""create account companies

Revision ID: 2c6a9cfac413
Revises: 1dd364afc06c
Create Date: 2025-10-13 20:58:18.201426

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c6a9cfac413"
down_revision: Union[str, Sequence[str], None] = "1dd364afc06c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(), index=True),
    )


def downgrade():
    op.drop_table("companies")
