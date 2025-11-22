"""add no_send_settings table

Revision ID: a1b2c3d4e5f6
Revises: 69cedf41891c
Create Date: 2025-11-21 00:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '69cedf41891c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Phase3: 送信禁止設定テーブル ###

    # no_send_settingsテーブル作成
    op.create_table(
        'no_send_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False, comment='リストID'),
        sa.Column('setting_type', sa.String(length=50), nullable=False,
                  comment='設定種別 (day_of_week/time_range/specific_date)'),
        sa.Column('name', sa.String(length=255), nullable=False,
                  comment='設定名'),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='設定の説明'),
        sa.Column('is_enabled', sa.Boolean(), server_default='true', nullable=False,
                  comment='設定の有効/無効'),
        sa.Column('day_of_week_list', postgresql.ARRAY(sa.Integer()), nullable=True,
                  comment='送信禁止曜日リスト [1=月,2=火,...,7=日]'),
        sa.Column('time_start', sa.Time(), nullable=True,
                  comment='送信禁止開始時刻'),
        sa.Column('time_end', sa.Time(), nullable=True,
                  comment='送信禁止終了時刻'),
        sa.Column('specific_date', sa.Date(), nullable=True,
                  comment='送信禁止日'),
        sa.Column('date_range_start', sa.Date(), nullable=True,
                  comment='送信禁止期間開始日'),
        sa.Column('date_range_end', sa.Date(), nullable=True,
                  comment='送信禁止期間終了日'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # インデックス作成
    op.create_index(op.f('ix_no_send_settings_list_id'),
                    'no_send_settings', ['list_id'], unique=False)
    op.create_index(op.f('ix_no_send_settings_setting_type'),
                    'no_send_settings', ['setting_type'], unique=False)
    op.create_index(op.f('ix_no_send_settings_specific_date'),
                    'no_send_settings', ['specific_date'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Phase3: 送信禁止設定テーブル削除 ###
    op.drop_index(op.f('ix_no_send_settings_specific_date'),
                  table_name='no_send_settings')
    op.drop_index(op.f('ix_no_send_settings_setting_type'),
                  table_name='no_send_settings')
    op.drop_index(op.f('ix_no_send_settings_list_id'),
                  table_name='no_send_settings')
    op.drop_table('no_send_settings')
    # ### end Alembic commands ###
