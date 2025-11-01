"""Initial schema - Phase 1: User, Organization, Role, Permission tables

Revision ID: 20251102_0000
Revises:
Create Date: 2025-11-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251102_0000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # organizationsテーブルの作成
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='組織名'),
        sa.Column(
            'type',
            sa.Enum('sales_support', 'client', name='organization_type'),
            nullable=False,
            comment='組織タイプ（営業支援会社/顧客企業）',
        ),
        sa.Column(
            'parent_organization_id',
            sa.Integer(),
            nullable=True,
            comment='親組織ID（顧客企業の場合、担当する営業支援会社のID）',
        ),
        sa.Column('email', sa.String(length=255), nullable=True, comment='代表メール'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='代表電話番号'),
        sa.Column('address', sa.Text(), nullable=True, comment='住所'),
        sa.Column('description', sa.Text(), nullable=True, comment='備考'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # usersテーブルの作成
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False, comment='所属組織ID'),
        sa.Column(
            'email',
            sa.String(length=255),
            nullable=False,
            comment='メールアドレス（ログインID）',
        ),
        sa.Column('hashed_password', sa.String(length=255), nullable=False, comment='ハッシュ化パスワード'),
        sa.Column('full_name', sa.String(length=255), nullable=False, comment='氏名'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='電話番号'),
        sa.Column('avatar_url', sa.String(length=500), nullable=True, comment='プロフィール画像URL'),
        sa.Column('description', sa.Text(), nullable=True, comment='備考'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='アクティブフラグ'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='メール認証済みフラグ'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_organization_id', 'users', ['organization_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # rolesテーブルの作成
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, comment='ロール名（一意）'),
        sa.Column('display_name', sa.String(length=100), nullable=False, comment='表示名'),
        sa.Column('description', sa.Text(), nullable=True, comment='説明'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_roles_name', 'roles', ['name'])

    # permissionsテーブルの作成
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('resource', sa.String(length=50), nullable=False, comment='リソース名（例: project, list, worker）'),
        sa.Column('action', sa.String(length=50), nullable=False, comment='アクション名（例: create, read, update, delete）'),
        sa.Column('description', sa.Text(), nullable=True, comment='説明'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )
    op.create_index('ix_permissions_resource', 'permissions', ['resource'])
    op.create_index('ix_permissions_action', 'permissions', ['action'])

    # user_rolesテーブルの作成
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='ユーザーID'),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='ロールID'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])

    # role_permissionsテーブルの作成
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False, comment='ロールID'),
        sa.Column('permission_id', sa.Integer(), nullable=False, comment='権限ID'),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['role_id'])
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['permission_id'])

    # 初期データの投入（ロール）
    op.execute(
        """
        INSERT INTO roles (name, display_name, description) VALUES
        ('sales_support', '営業支援会社', '営業支援を提供する会社の担当者'),
        ('client', '顧客', '営業支援を依頼するクライアント企業の担当者'),
        ('worker', 'ワーカー', 'フォーム営業の実務作業者');
        """
    )


def downgrade() -> None:
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('organizations')
    op.execute('DROP TYPE organization_type')
