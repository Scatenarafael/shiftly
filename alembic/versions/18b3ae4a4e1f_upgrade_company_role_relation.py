"""upgrade company role relation

Revision ID: 18b3ae4a4e1f
Revises: f504067f3889
Create Date: 2025-11-20 15:59:06.265029

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18b3ae4a4e1f"
down_revision: Union[str, Sequence[str], None] = "f504067f3889"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # adiciona coluna company_id na tabela roles
    op.add_column(
        "roles",
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,  # coloque False se você já tiver dados coerentes para todas as linhas
        ),
    )

    # cria a FK roles.company_id -> companies.id com ON DELETE CASCADE
    op.create_foreign_key(
        "fk_roles_company_id",
        source_table="roles",
        referent_table="companies",
        local_cols=["company_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # desfaz a FK e a coluna
    op.drop_constraint("fk_roles_company_id", "roles", type_="foreignkey")
    op.drop_column("roles", "company_id")
