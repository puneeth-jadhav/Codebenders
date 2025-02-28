"""add_tech_bundle_id_to_projects

Revision ID: f4939e7d9dc0
Revises: c22aaac6c97c
Create Date: 2025-02-23 13:07:24.802543

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4939e7d9dc0"
down_revision: Union[str, None] = "c22aaac6c97c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add tech_bundle_id column
    op.add_column("projects", sa.Column("tech_bundle_id", sa.String(24), nullable=True))
    # Add index for tech_bundle_id
    op.create_index("ix_projects_tech_bundle_id", "projects", ["tech_bundle_id"])


def downgrade() -> None:
    # Remove index
    op.drop_index("ix_projects_tech_bundle_id", table_name="projects")
    # Remove column
    op.drop_column("projects", "tech_bundle_id")
