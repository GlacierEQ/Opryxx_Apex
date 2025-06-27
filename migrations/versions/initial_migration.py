""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-06-26 18:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create todo_categories table
    op.create_table(
        'todo_categories',
        sa.Column('id', sa.String(36), nullable=False, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sqlite_autoincrement=True
    )

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.String(36), nullable=False, primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('priority', sa.Enum('critical', 'high', 'medium', 'low', name='priority_enum'), 
                 nullable=False, server_default='medium'),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'archived', 'failed', 
                                  name='todo_status_enum'), 
                 nullable=False, server_default='pending'),
        sa.Column('due_date', sa.DateTime, nullable=True, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), 
                 onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('tags', sa.JSON, nullable=False, server_default='[]'),
        sa.Column('metadata_', sa.JSON, nullable=False, server_default='{}'),
        sa.Column('category_id', sa.String(36), sa.ForeignKey('todo_categories.id'), index=True),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('todos.id'), index=True),
        sqlite_autoincrement=True
    )
    
    # Create indexes for todos
    op.create_index('idx_todo_status_priority', 'todos', ['status', 'priority', 'due_date'])
    
    # Create todo_subtasks table
    op.create_table(
        'todo_subtasks',
        sa.Column('id', sa.String(36), nullable=False, primary_key=True),
        sa.Column('todo_id', sa.String(36), sa.ForeignKey('todos.id'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('completed', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), 
                 onupdate=sa.func.now()),
        sqlite_autoincrement=True
    )
    
    # Create todo_processing_logs table
    op.create_table(
        'todo_processing_logs',
        sa.Column('id', sa.String(36), nullable=False, primary_key=True),
        sa.Column('todo_id', sa.String(36), sa.ForeignKey('todos.id'), nullable=False, index=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
        sa.Column('status', sa.Enum('queued', 'processing', 'processed', 'error', 
                                   name='processing_status_enum'), 
                 nullable=False, server_default='queued'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sqlite_autoincrement=True
    )
    
    # Create indexes for processing logs
    op.create_index('idx_processing_logs_todo_id', 'todo_processing_logs', ['todo_id'])
    op.create_index('idx_processing_logs_status', 'todo_processing_logs', ['status'])
    op.create_index('idx_processing_logs_created_at', 'todo_processing_logs', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('todo_processing_logs')
    op.drop_table('todo_subtasks')
    op.drop_table('todos')
    op.drop_table('todo_categories')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS priority_enum")
    op.execute("DROP TYPE IF EXISTS todo_status_enum")
    op.execute("DROP TYPE IF EXISTS processing_status_enum")
