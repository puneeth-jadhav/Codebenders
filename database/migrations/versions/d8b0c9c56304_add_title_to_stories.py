"""add_title_to_stories

Revision ID: d8b0c9c56304
Revises: 79bf4899c832
Create Date: 2025-02-26 15:02:43.094196

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d8b0c9c56304"
down_revision: Union[str, None] = "79bf4899c832"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add title column
    op.add_column("stories", sa.Column("title", sa.String(200), nullable=True))

    # Make it non-nullable after adding to existing rows
    op.execute("UPDATE stories SET title = 'Story ' || id WHERE title IS NULL")
    op.alter_column("stories", "title", nullable=False)


def downgrade() -> None:
    # Remove title column
    op.drop_column("stories", "title")
