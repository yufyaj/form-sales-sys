"""add list_item_assignments table for worker assignment

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-11-22 16:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """list_item_assignmentsテーブルの作成"""

    # テーブル作成
    op.create_table(
        'list_item_assignments',
        # プライマリキー
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # 外部キー
        sa.Column('list_item_id', sa.Integer(), nullable=False,
                  comment='リスト項目ID'),
        sa.Column('worker_id', sa.Integer(), nullable=False,
                  comment='ワーカーID'),

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

        # 制約定義
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['list_item_id'],
            ['list_items.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['worker_id'],
            ['workers.id'],
            ondelete='CASCADE'
        ),
        # 重複割り当て防止: 同じリスト項目に同じワーカーを複数回割り当てできない
        sa.UniqueConstraint('list_item_id', 'worker_id', name='uq_list_item_worker'),
    )

    # インデックス作成
    op.create_index(
        'ix_list_item_assignments_list_item_id',
        'list_item_assignments',
        ['list_item_id']
    )
    op.create_index(
        'ix_list_item_assignments_worker_id',
        'list_item_assignments',
        ['worker_id']
    )

    # updated_at自動更新トリガーの作成
    # SQLAlchemyのORM経由でない直接のSQL更新でも確実にupdated_atが更新されるようにする
    op.execute("""
        CREATE OR REPLACE FUNCTION update_list_item_assignments_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_list_item_assignments_updated_at
        BEFORE UPDATE ON list_item_assignments
        FOR EACH ROW
        EXECUTE FUNCTION update_list_item_assignments_updated_at();
    """)


def downgrade() -> None:
    """list_item_assignmentsテーブルの削除"""

    # トリガーと関数を削除
    op.execute("DROP TRIGGER IF EXISTS trigger_update_list_item_assignments_updated_at ON list_item_assignments;")
    op.execute("DROP FUNCTION IF EXISTS update_list_item_assignments_updated_at();")

    # インデックス削除（テーブル削除前に明示的に削除するのがベストプラクティス）
    op.drop_index('ix_list_item_assignments_worker_id', table_name='list_item_assignments')
    op.drop_index('ix_list_item_assignments_list_item_id', table_name='list_item_assignments')

    # テーブル削除
    op.drop_table('list_item_assignments')
