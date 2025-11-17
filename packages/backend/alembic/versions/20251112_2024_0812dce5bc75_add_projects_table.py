"""add projects table

Revision ID: 0812dce5bc75
Revises: 0d9ad76f670b
Create Date: 2025-11-12 20:24:30.385566+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0812dce5bc75'
down_revision: Union[str, None] = '0d9ad76f670b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum型の作成
    project_status_enum = sa.Enum(
        'planning', 'in_progress', 'on_hold', 'completed', 'cancelled',
        name='project_status'
    )
    project_priority_enum = sa.Enum(
        'low', 'medium', 'high', 'critical',
        name='project_priority'
    )

    project_status_enum.create(op.get_bind())
    project_priority_enum.create(op.get_bind())

    # テーブルの作成
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_organization_id', sa.Integer(), nullable=False,
                  comment='顧客組織ID'),
        sa.Column('name', sa.String(length=255), nullable=False,
                  comment='プロジェクト名'),
        sa.Column('status', project_status_enum, nullable=False,
                  server_default='planning',
                  comment='プロジェクトステータス'),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='プロジェクト説明'),
        sa.Column('start_date', sa.Date(), nullable=True,
                  comment='開始予定日'),
        sa.Column('end_date', sa.Date(), nullable=True,
                  comment='終了予定日'),
        sa.Column('estimated_budget', sa.BigInteger(), nullable=True,
                  comment='見積予算（円）'),
        sa.Column('actual_budget', sa.BigInteger(), nullable=True,
                  comment='実績予算（円）'),
        sa.Column('priority', project_priority_enum, nullable=True,
                  comment='プロジェクト優先度'),
        sa.Column('owner_user_id', sa.Integer(), nullable=True,
                  comment='プロジェクトオーナー（担当ユーザー）'),
        sa.Column('notes', sa.Text(), nullable=True, comment='備考'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_organization_id'],
                                ['client_organizations.id'],
                                ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['owner_user_id'],
                                ['users.id'],
                                ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # インデックスの作成
    op.create_index(
        op.f('ix_projects_client_organization_id'),
        'projects',
        ['client_organization_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_projects_status'),
        'projects',
        ['status'],
        unique=False
    )
    op.create_index(
        op.f('ix_projects_owner_user_id'),
        'projects',
        ['owner_user_id'],
        unique=False
    )


def downgrade() -> None:
    # インデックスの削除
    op.drop_index(op.f('ix_projects_owner_user_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_index(op.f('ix_projects_client_organization_id'),
                  table_name='projects')

    # テーブルの削除
    op.drop_table('projects')

    # Enum型の削除
    sa.Enum(name='project_status').drop(op.get_bind())
    sa.Enum(name='project_priority').drop(op.get_bind())
