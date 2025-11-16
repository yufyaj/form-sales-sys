"""add list management tables for phase3

Revision ID: 69cedf41891c
Revises: 0d9ad76f670b
Create Date: 2025-11-16 23:17:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '69cedf41891c'
down_revision: Union[str, None] = '0d9ad76f670b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Phase3: リスト管理テーブル ###

    # listsテーブル
    op.create_table('lists',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False, comment='営業支援会社のID（マルチテナント対応）'),
    sa.Column('name', sa.String(length=255), nullable=False, comment='リスト名'),
    sa.Column('description', sa.Text(), nullable=True, comment='リストの説明'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lists_organization_id'), 'lists', ['organization_id'], unique=False)

    # custom_column_settingsテーブル
    op.create_table('custom_column_settings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=False, comment='リストID'),
    sa.Column('column_name', sa.String(length=100), nullable=False, comment='カラム識別子（一意な名前、プログラムで使用）'),
    sa.Column('display_name', sa.String(length=255), nullable=False, comment='カラム表示名（UI用）'),
    sa.Column('column_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='カラム設定（型、検証ルール、オプションなどをJSONで管理）'),
    sa.Column('display_order', sa.Integer(), nullable=False, comment='表示順序'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('list_id', 'column_name', name='uq_custom_column_settings_list_id_column_name')
    )
    op.create_index(op.f('ix_custom_column_settings_list_id'), 'custom_column_settings', ['list_id'], unique=False)
    # JSONBカラムにGINインデックスを作成（高速検索用）
    op.create_index('ix_custom_column_settings_column_config', 'custom_column_settings', ['column_config'], unique=False, postgresql_using='gin')

    # list_itemsテーブル
    op.create_table('list_items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=False, comment='リストID'),
    sa.Column('title', sa.String(length=500), nullable=False, comment='企業名などのタイトル'),
    sa.Column('status', sa.String(length=50), server_default='pending', nullable=False, comment='ステータス（pending, contacted, negotiatingなど）'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_list_items_list_id'), 'list_items', ['list_id'], unique=False)

    # list_item_custom_valuesテーブル
    op.create_table('list_item_custom_values',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('list_item_id', sa.Integer(), nullable=False, comment='リスト項目ID'),
    sa.Column('custom_column_setting_id', sa.Integer(), nullable=False, comment='カスタムカラム設定ID'),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='カスタムカラムの値（文字列、数値、真偽値、配列などをJSONで管理）'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['custom_column_setting_id'], ['custom_column_settings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['list_item_id'], ['list_items.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('list_item_id', 'custom_column_setting_id', name='uq_list_item_custom_values_list_item_id_custom_column_setting_id')
    )
    op.create_index(op.f('ix_list_item_custom_values_custom_column_setting_id'), 'list_item_custom_values', ['custom_column_setting_id'], unique=False)
    op.create_index(op.f('ix_list_item_custom_values_list_item_id'), 'list_item_custom_values', ['list_item_id'], unique=False)
    # JSONBカラムにGINインデックスを作成（高速検索用）
    op.create_index('ix_list_item_custom_values_value', 'list_item_custom_values', ['value'], unique=False, postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Phase3: リスト管理テーブル削除 ###
    op.drop_index('ix_list_item_custom_values_value', table_name='list_item_custom_values')
    op.drop_index(op.f('ix_list_item_custom_values_list_item_id'), table_name='list_item_custom_values')
    op.drop_index(op.f('ix_list_item_custom_values_custom_column_setting_id'), table_name='list_item_custom_values')
    op.drop_table('list_item_custom_values')
    op.drop_index(op.f('ix_list_items_list_id'), table_name='list_items')
    op.drop_table('list_items')
    op.drop_index('ix_custom_column_settings_column_config', table_name='custom_column_settings')
    op.drop_index(op.f('ix_custom_column_settings_list_id'), table_name='custom_column_settings')
    op.drop_table('custom_column_settings')
    op.drop_index(op.f('ix_lists_organization_id'), table_name='lists')
    op.drop_table('lists')
    # ### end Alembic commands ###
