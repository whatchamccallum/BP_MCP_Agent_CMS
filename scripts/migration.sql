"""Alembic migration script for BP_MCP_Agent_CMS."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Import any custom types or enum definitions if needed
# from api.models import CustomType, CustomEnum

def upgrade():
    """
    Perform database upgrade operations.
    This is where you define the schema changes for your migration.
    """
    # User table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), unique=True, nullable=False),
        sa.Column('email', sa.String(length=120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Test Environment table
    op.create_table('test_environments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Devices Under Test (DUT) table
    op.create_table('devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('serial_number', sa.String(length=50), unique=True, nullable=True),
        sa.Column('environment_id', sa.Integer(), sa.ForeignKey('test_environments.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),  # e.g., 'active', 'inactive', 'maintenance'
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Test Configuration table
    op.create_table('test_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('configuration_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Test Runs table
    op.create_table('test_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('configuration_id', sa.Integer(), sa.ForeignKey('test_configurations.id'), nullable=False),
        sa.Column('environment_id', sa.Integer(), sa.ForeignKey('test_environments.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),  # e.g., 'pending', 'running', 'completed', 'failed'
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('result_summary', postgresql.JSONB(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Media Files table
    op.create_table('media_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('test_run_id', sa.Integer(), sa.ForeignKey('test_runs.id'), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Reports table
    op.create_table('reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_run_id', sa.Integer(), sa.ForeignKey('test_runs.id'), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_data', postgresql.JSONB(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('generated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    """
    Perform database downgrade operations.
    Reverse the upgrade steps to allow rolling back migrations.
    """
    # Drop tables in reverse order of creation
    op.drop_table('reports')
    op.drop_table('media_files')
    op.drop_table('test_runs')
    op.drop_table('test_configurations')
    op.drop_table('devices')
    op.drop_table('test_environments')
    op.drop_table('users')