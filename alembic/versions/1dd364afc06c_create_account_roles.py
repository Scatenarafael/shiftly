"""create account roles

Revision ID: 1dd364afc06c
Revises: c14203442612
Create Date: 2025-10-13 20:56:31.525170

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1dd364afc06c"
down_revision: Union[str, Sequence[str], None] = "c14203442612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table("roles")
