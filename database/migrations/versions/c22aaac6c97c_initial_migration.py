"""Initial migration

Revision ID: c22aaac6c97c
Revises: 
Create Date: 2025-02-20 19:38:22.768242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c22aaac6c97c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=2048)),
        sa.Column("mongo_content_id", sa.String(length=24), index=True),  # MongoDB ObjectId as string
    )

    # Create features table
    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.Enum("EXTRACTED", "SUGGESTED", name="featuretypeenum"), nullable=False),
        sa.Column("is_finalized", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("mongo_summary_id", sa.String(length=24), index=True),
    )

    # Create epics table
    op.create_table(
        "epics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("feature_id", sa.Integer(), sa.ForeignKey("features.id"), unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("mongo_description_id", sa.String(length=24), index=True),
    )

    # Create stories table
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("epic_id", sa.Integer(), sa.ForeignKey("epics.id"), nullable=False),
        sa.Column("mongo_description_id", sa.String(length=24), index=True),
    )

    # Create data_models table
    op.create_table(
        "data_models",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("table_name", sa.String(length=100), nullable=False, unique=False),
    )

    # Create data_columns table
    op.create_table(
        "data_columns",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("table_id", sa.Integer(), sa.ForeignKey("data_models.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(length=100), nullable=False),
        sa.Column("column_type", sa.String(length=255), nullable=False),
        sa.Column("is_nullable", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("relationships", sa.String(length=255)),
        sa.Column("is_unique", sa.Boolean(), server_default=sa.text("0")),
    )

def downgrade() -> None:
    # Drop tables in reverse order of creation to avoid foreign key constraints issues
    op.drop_table("stories")
    op.drop_table("epics")
    op.drop_table("features")
    op.drop_table("data_columns")
    op.drop_table("data_models")
    op.drop_table("projects")

