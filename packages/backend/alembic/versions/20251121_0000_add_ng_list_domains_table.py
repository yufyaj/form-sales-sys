"""add ng_list_domains table for phase3

Revision ID: a1b2c3d4e5f6
Revises: 69cedf41891c
Create Date: 2025-11-21 00:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '69cedf41891c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Phase3: NGリスト管理テーブル ###

    # ng_list_domainsテーブル
    op.create_table('ng_list_domains',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('list_id', sa.Integer(), nullable=False, comment='リストID（FK to lists.id）'),
    sa.Column('domain', sa.String(length=255), nullable=False, comment='元のドメインパターン（ユーザー入力）'),
    sa.Column('domain_pattern', sa.String(length=255), nullable=False, comment='正規化されたドメインパターン（比較用）'),
    sa.Column('is_wildcard', sa.Boolean(), server_default='false', nullable=False, comment='ワイルドカード使用フラグ'),
    sa.Column('memo', sa.Text(), nullable=True, comment='メモ（任意）'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('list_id', 'domain_pattern', name='uq_ng_list_domains_list_id_domain_pattern')
    )
    op.create_index(op.f('ix_ng_list_domains_list_id'), 'ng_list_domains', ['list_id'], unique=False)
    op.create_index(op.f('ix_ng_list_domains_domain_pattern'), 'ng_list_domains', ['domain_pattern'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### Phase3: NGリスト管理テーブル削除 ###
    op.drop_index(op.f('ix_ng_list_domains_domain_pattern'), table_name='ng_list_domains')
    op.drop_index(op.f('ix_ng_list_domains_list_id'), table_name='ng_list_domains')
    op.drop_table('ng_list_domains')
    # ### end Alembic commands ###
