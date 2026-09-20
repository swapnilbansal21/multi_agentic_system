"""create officers table

Revision ID: f3eca06f2b32
Revises: 
Create Date: 2026-09-20 00:47:17.143509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f3eca06f2b32'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "officers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("department", sa.String(length=200), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
    )
    op.create_unique_constraint("uq_officers_email", "officers", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("officers")
