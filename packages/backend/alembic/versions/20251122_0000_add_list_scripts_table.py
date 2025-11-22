"""add list_scripts table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-22 00:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Phase4: スクリプト管理テーブル ###

    # list_scriptsテーブル作成
    op.create_table(
        'list_scripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False,
                  comment='リストID（外部キー）'),
        sa.Column('title', sa.String(length=255), nullable=False,
                  comment='スクリプトタイトル'),
        sa.Column('content', sa.Text(), nullable=False,
                  comment='スクリプト本文（営業トークの台本）'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # インデックス作成
    op.create_index(op.f('ix_list_scripts_list_id'),
                    'list_scripts', ['list_id'], unique=False)

    # 複合インデックス作成（論理削除を考慮したクエリ最適化）
    # WHERE list_id = ? AND deleted_at IS NULL のようなクエリのパフォーマンス向上
    op.create_index('ix_list_scripts_list_id_deleted_at',
                    'list_scripts', ['list_id', 'deleted_at'], unique=False)

    # updated_at自動更新トリガーの作成
    # SQLAlchemyのORM経由でない直接のSQL更新でも確実にupdated_atが更新されるようにする
    op.execute("""
        CREATE OR REPLACE FUNCTION update_list_scripts_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_list_scripts_updated_at
        BEFORE UPDATE ON list_scripts
        FOR EACH ROW
        EXECUTE FUNCTION update_list_scripts_updated_at();
    """)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Phase4: スクリプト管理テーブル削除 ###

    # トリガーと関数を削除
    op.execute("DROP TRIGGER IF EXISTS trigger_update_list_scripts_updated_at ON list_scripts;")
    op.execute("DROP FUNCTION IF EXISTS update_list_scripts_updated_at();")

    # インデックス削除
    op.drop_index('ix_list_scripts_list_id_deleted_at',
                  table_name='list_scripts')
    op.drop_index(op.f('ix_list_scripts_list_id'),
                  table_name='list_scripts')

    # テーブル削除
    op.drop_table('list_scripts')
    # ### end Alembic commands ###
