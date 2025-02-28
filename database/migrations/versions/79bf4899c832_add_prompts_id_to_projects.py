"""add_prompts_id_to_projects

Revision ID: 79bf4899c832
Revises: 5acf220bc390
Create Date: 2025-02-26 10:50:49.575316

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "79bf4899c832"
down_revision: Union[str, None] = "5acf220bc390"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add prompts_id column
    op.add_column("projects", sa.Column("prompts_id", sa.String(24), nullable=True))
    # Add index for prompts_id
    op.create_index("ix_projects_prompts_id", "projects", ["prompts_id"])


def downgrade() -> None:
    # Remove index
    op.drop_index("ix_projects_prompts_id", table_name="projects")
    # Remove column
    op.drop_column("projects", "prompts_id")
