"""add_theme_id_to_projects

Revision ID: 5acf220bc390
Revises: f4939e7d9dc0
Create Date: 2025-02-25 20:24:13.361088

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5acf220bc390"
down_revision: Union[str, None] = "f4939e7d9dc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add theme_id column
    op.add_column("projects", sa.Column("theme_id", sa.String(24), nullable=True))
    # Add index for theme_id
    op.create_index("ix_projects_theme_id", "projects", ["theme_id"])


def downgrade() -> None:
    # Remove index
    op.drop_index("ix_projects_theme_id", table_name="projects")
    # Remove column
    op.drop_column("projects", "theme_id")
