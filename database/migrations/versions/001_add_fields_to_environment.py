"""add fields to environment

Revision ID: 001
Revises: 
Create Date: 2025-03-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to environments table
    op.add_column('environments', sa.Column('ip_address', sa.String(100), nullable=True))
    op.add_column('environments', sa.Column('port', sa.Integer(), nullable=True))
    op.add_column('environments', sa.Column('username', sa.String(100), nullable=True))
    op.add_column('environments', sa.Column('password', sa.String(100), nullable=True))
    op.add_column('environments', sa.Column('is_active', sa.Boolean(), default=True, nullable=True))
    op.add_column('environments', sa.Column('created_by', sa.String(100), nullable=True))
    op.add_column('environments', sa.Column('updated_by', sa.String(100), nullable=True))


def downgrade():
    # Drop the added columns
    op.drop_column('environments', 'ip_address')
    op.drop_column('environments', 'port')
    op.drop_column('environments', 'username')
    op.drop_column('environments', 'password')
    op.drop_column('environments', 'is_active')
    op.drop_column('environments', 'created_by')
    op.drop_column('environments', 'updated_by')
