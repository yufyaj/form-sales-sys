"""Add list status column

Revision ID: add_list_status
Revises: 20251121_0000_add_no_send_settings_table
Create Date: 2025-11-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_list_status"
down_revision = "20251121_0000_add_no_send_settings_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """リストステータスカラムを追加"""
    # ENUMタイプを作成
    list_status_enum = postgresql.ENUM(
        "draft", "submitted", "accepted", "rejected", name="liststatus", create_type=True
    )
    list_status_enum.create(op.get_bind(), checkfirst=True)

    # listsテーブルにstatusカラムを追加
    op.add_column(
        "lists",
        sa.Column(
            "status",
            postgresql.ENUM("draft", "submitted", "accepted", "rejected", name="liststatus"),
            nullable=False,
            server_default="draft",
            comment="リストステータス(draft/submitted/accepted/rejected)",
        ),
    )


def downgrade() -> None:
    """リストステータスカラムを削除"""
    # listsテーブルからstatusカラムを削除
    op.drop_column("lists", "status")

    # ENUMタイプを削除
    sa.Enum(name="liststatus").drop(op.get_bind(), checkfirst=True)
