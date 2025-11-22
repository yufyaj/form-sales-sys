"""Add work records and cannot send reasons tables

Revision ID: add_work_records_tables
Revises: c3d4e5f6a7b8
Create Date: 2025-11-22 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_work_records_tables'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """作業記録関連テーブルの作成"""

    # 送信不可理由マスターテーブルを先に作成（work_recordsから参照されるため）
    op.create_table(
        'cannot_send_reasons',
        # プライマリキー
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # 理由情報
        sa.Column('reason_code', sa.String(length=100), nullable=False,
                  comment='理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）'),
        sa.Column('reason_name', sa.String(length=255), nullable=False,
                  comment='理由名'),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='詳細説明'),

        # 有効/無効フラグ
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true',
                  comment='有効/無効フラグ'),

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
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        # 制約定義
        sa.PrimaryKeyConstraint('id'),
        # 理由コードはユニーク（論理削除対応のため、deleted_atがNULLのものに限定）
        sa.UniqueConstraint('reason_code', name='uq_cannot_send_reasons_reason_code',
                           postgresql_where=sa.text('deleted_at IS NULL')),
    )

    # インデックス作成
    op.create_index(
        'ix_cannot_send_reasons_reason_code',
        'cannot_send_reasons',
        ['reason_code']
    )
    op.create_index(
        'ix_cannot_send_reasons_is_active',
        'cannot_send_reasons',
        ['is_active']
    )

    # 作業記録ステータスのEnum型を作成
    op.execute(
        """
        CREATE TYPE work_record_status AS ENUM ('sent', 'cannot_send')
        """
    )

    # 作業記録テーブルの作成
    op.create_table(
        'work_records',
        # プライマリキー
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # 外部キー
        sa.Column('assignment_id', sa.Integer(), nullable=False,
                  comment='リスト項目割り当てID'),
        sa.Column('worker_id', sa.Integer(), nullable=False,
                  comment='ワーカーID'),

        # ステータス
        sa.Column(
            'status',
            sa.Enum('sent', 'cannot_send', name='work_record_status'),
            nullable=False,
            comment='送信済みまたは送信不可',
        ),

        # 日時情報
        sa.Column(
            'started_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='作業開始日時',
        ),
        sa.Column(
            'completed_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='作業完了日時',
        ),

        # 送信結果詳細（JSON形式）
        sa.Column(
            'form_submission_result',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='送信結果の詳細（JSONフィールド）',
        ),

        # 送信不可理由（送信不可の場合のみ）
        sa.Column('cannot_send_reason_id', sa.Integer(), nullable=True,
                  comment='送信不可理由ID（送信不可の場合のみ）'),

        # メモ・備考
        sa.Column('notes', sa.Text(), nullable=True,
                  comment='メモ・備考'),

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
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        # 制約定義
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['assignment_id'],
            ['list_item_assignments.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['worker_id'],
            ['workers.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['cannot_send_reason_id'],
            ['cannot_send_reasons.id'],
            ondelete='SET NULL'
        ),
    )

    # インデックス作成
    op.create_index(
        'ix_work_records_assignment_id',
        'work_records',
        ['assignment_id']
    )
    op.create_index(
        'ix_work_records_worker_id',
        'work_records',
        ['worker_id']
    )
    op.create_index(
        'ix_work_records_status',
        'work_records',
        ['status']
    )
    op.create_index(
        'ix_work_records_started_at',
        'work_records',
        ['started_at']
    )
    op.create_index(
        'ix_work_records_completed_at',
        'work_records',
        ['completed_at']
    )

    # updated_at自動更新トリガーの作成（cannot_send_reasons用）
    op.execute("""
        CREATE OR REPLACE FUNCTION update_cannot_send_reasons_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_cannot_send_reasons_updated_at
        BEFORE UPDATE ON cannot_send_reasons
        FOR EACH ROW
        EXECUTE FUNCTION update_cannot_send_reasons_updated_at();
    """)

    # updated_at自動更新トリガーの作成（work_records用）
    op.execute("""
        CREATE OR REPLACE FUNCTION update_work_records_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trigger_update_work_records_updated_at
        BEFORE UPDATE ON work_records
        FOR EACH ROW
        EXECUTE FUNCTION update_work_records_updated_at();
    """)


def downgrade() -> None:
    """作業記録関連テーブルの削除"""

    # work_recordsテーブルのトリガーと関数を削除
    op.execute("DROP TRIGGER IF EXISTS trigger_update_work_records_updated_at ON work_records;")
    op.execute("DROP FUNCTION IF EXISTS update_work_records_updated_at();")

    # cannot_send_reasonsテーブルのトリガーと関数を削除
    op.execute("DROP TRIGGER IF EXISTS trigger_update_cannot_send_reasons_updated_at ON cannot_send_reasons;")
    op.execute("DROP FUNCTION IF EXISTS update_cannot_send_reasons_updated_at();")

    # work_recordsテーブルのインデックス削除
    op.drop_index('ix_work_records_completed_at', table_name='work_records')
    op.drop_index('ix_work_records_started_at', table_name='work_records')
    op.drop_index('ix_work_records_status', table_name='work_records')
    op.drop_index('ix_work_records_worker_id', table_name='work_records')
    op.drop_index('ix_work_records_assignment_id', table_name='work_records')

    # work_recordsテーブル削除
    op.drop_table('work_records')

    # Enum型削除
    op.execute("DROP TYPE IF EXISTS work_record_status")

    # cannot_send_reasonsテーブルのインデックス削除
    op.drop_index('ix_cannot_send_reasons_is_active', table_name='cannot_send_reasons')
    op.drop_index('ix_cannot_send_reasons_reason_code', table_name='cannot_send_reasons')

    # cannot_send_reasonsテーブル削除
    op.drop_table('cannot_send_reasons')
