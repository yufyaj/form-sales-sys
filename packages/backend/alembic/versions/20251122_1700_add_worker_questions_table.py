"""add worker_questions table for Phase5

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2025-11-22 17:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """worker_questionsテーブルの作成"""

    # Enumタイプの作成
    op.execute("""
        CREATE TYPE question_status AS ENUM ('pending', 'in_review', 'answered', 'closed');
    """)

    op.execute("""
        CREATE TYPE question_priority AS ENUM ('low', 'medium', 'high', 'urgent');
    """)

    # テーブル作成
    op.create_table(
        'worker_questions',
        # プライマリキー
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # 外部キー
        sa.Column('worker_id', sa.Integer(), nullable=False,
                  comment='質問者のワーカーID'),
        sa.Column('organization_id', sa.Integer(), nullable=False,
                  comment='営業支援会社の組織ID（マルチテナントキー）'),
        sa.Column('client_organization_id', sa.Integer(), nullable=True,
                  comment='関連する顧客組織ID（オプション）'),
        sa.Column('answered_by_user_id', sa.Integer(), nullable=True,
                  comment='回答者のユーザーID'),

        # 質問内容
        sa.Column('title', sa.String(500), nullable=False,
                  comment='質問タイトル'),
        sa.Column('content', sa.Text(), nullable=False,
                  comment='質問内容'),

        # ステータス管理
        sa.Column('status', sa.Enum('pending', 'in_review', 'answered', 'closed',
                                    name='question_status', create_type=False),
                  nullable=False, server_default='pending',
                  comment='質問ステータス'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent',
                                      name='question_priority', create_type=False),
                  nullable=False, server_default='medium',
                  comment='質問優先度'),

        # 回答情報
        sa.Column('answer', sa.Text(), nullable=True,
                  comment='回答内容'),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True,
                  comment='回答日時'),

        # メタデータ
        sa.Column('tags', sa.Text(), nullable=True,
                  comment='タグ（JSON配列形式）'),
        sa.Column('internal_notes', sa.Text(), nullable=True,
                  comment='営業支援会社用の内部メモ'),

        # タイムスタンプ
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

        # ソフトデリート
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        # 制約定義
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['worker_id'],
            ['workers.id'],
            ondelete='RESTRICT'
        ),
        sa.ForeignKeyConstraint(
            ['organization_id'],
            ['organizations.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['client_organization_id'],
            ['client_organizations.id'],
            ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['answered_by_user_id'],
            ['users.id'],
            ondelete='SET NULL'
        ),
    )

    # 基本インデックス作成
    op.create_index(
        'ix_worker_questions_worker_id',
        'worker_questions',
        ['worker_id']
    )
    op.create_index(
        'ix_worker_questions_organization_id',
        'worker_questions',
        ['organization_id']
    )
    op.create_index(
        'ix_worker_questions_client_organization_id',
        'worker_questions',
        ['client_organization_id']
    )
    op.create_index(
        'ix_worker_questions_status',
        'worker_questions',
        ['status']
    )

    # 複合インデックス作成（パフォーマンス最適化）
    # 営業支援会社スタッフが未読質問を高速取得するため
    op.create_index(
        'ix_worker_questions_org_status',
        'worker_questions',
        ['organization_id', 'status']
    )

    # ワーカーの質問履歴を時系列表示するため
    op.create_index(
        'ix_worker_questions_worker_created',
        'worker_questions',
        ['worker_id', 'created_at']
    )

    # 顧客企業別の質問フィルタリングのため
    op.create_index(
        'ix_worker_questions_client_org_status',
        'worker_questions',
        ['client_organization_id', 'status']
    )

    # updated_at自動更新トリガーの作成
    op.execute("""
        CREATE OR REPLACE FUNCTION update_worker_questions_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_worker_questions_updated_at
        BEFORE UPDATE ON worker_questions
        FOR EACH ROW
        EXECUTE FUNCTION update_worker_questions_updated_at();
    """)


def downgrade() -> None:
    """worker_questionsテーブルの削除"""

    # トリガーと関数を削除
    op.execute("DROP TRIGGER IF EXISTS trigger_update_worker_questions_updated_at ON worker_questions;")
    op.execute("DROP FUNCTION IF EXISTS update_worker_questions_updated_at();")

    # インデックス削除
    op.drop_index('ix_worker_questions_client_org_status', table_name='worker_questions')
    op.drop_index('ix_worker_questions_worker_created', table_name='worker_questions')
    op.drop_index('ix_worker_questions_org_status', table_name='worker_questions')
    op.drop_index('ix_worker_questions_status', table_name='worker_questions')
    op.drop_index('ix_worker_questions_client_organization_id', table_name='worker_questions')
    op.drop_index('ix_worker_questions_organization_id', table_name='worker_questions')
    op.drop_index('ix_worker_questions_worker_id', table_name='worker_questions')

    # テーブル削除
    op.drop_table('worker_questions')

    # Enumタイプの削除
    op.execute("DROP TYPE IF EXISTS question_priority;")
    op.execute("DROP TYPE IF EXISTS question_status;")
