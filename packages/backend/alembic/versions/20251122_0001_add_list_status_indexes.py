"""Add list status indexes

Revision ID: add_list_status_indexes
Revises: add_list_status
Create Date: 2025-11-22 00:01:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "add_list_status_indexes"
down_revision = "add_list_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """リストステータスのインデックスを追加してパフォーマンスを最適化"""
    # 単一カラムインデックス: statusでのフィルタリングを高速化
    op.create_index(
        "idx_lists_status",
        "lists",
        ["status"],
        unique=False,
    )

    # 複合インデックス: organization_idとstatusの組み合わせでの検索を最適化
    # 最も頻繁に使用されるクエリパターンに対応
    op.create_index(
        "idx_lists_org_status",
        "lists",
        ["organization_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    """インデックスを削除"""
    op.drop_index("idx_lists_org_status", table_name="lists")
    op.drop_index("idx_lists_status", table_name="lists")
