"""Add workers table

Revision ID: add_workers_table
Revises: add_list_status_indexes
Create Date: 2025-11-22 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_workers_table"
down_revision: Union[str, None] = "add_list_status_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """ワーカーテーブルを作成"""
    # Enum型を作成
    op.execute(
        """
        CREATE TYPE worker_status AS ENUM ('pending', 'active', 'inactive', 'suspended')
        """
    )
    op.execute(
        """
        CREATE TYPE skill_level AS ENUM ('beginner', 'intermediate', 'advanced', 'expert')
        """
    )

    # ワーカーテーブル作成
    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
            comment="対応するUserのID（1:1関係）",
        ),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
            comment="所属組織ID（営業支援会社）",
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "active", "inactive", "suspended", name="worker_status"),
            nullable=False,
            server_default="pending",
            comment="ワーカーステータス",
        ),
        sa.Column(
            "skill_level",
            sa.Enum("beginner", "intermediate", "advanced", "expert", name="skill_level"),
            nullable=True,
            comment="スキルレベル",
        ),
        sa.Column(
            "experience_months",
            sa.Integer(),
            nullable=True,
            comment="経験月数",
        ),
        sa.Column(
            "specialties",
            sa.Text(),
            nullable=True,
            comment="得意分野・専門領域（JSON配列またはカンマ区切り）",
        ),
        sa.Column(
            "max_tasks_per_day",
            sa.Integer(),
            nullable=True,
            comment="1日の最大タスク数",
        ),
        sa.Column(
            "available_hours_per_week",
            sa.Integer(),
            nullable=True,
            comment="週間稼働可能時間",
        ),
        sa.Column(
            "completed_tasks_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="完了タスク数",
        ),
        sa.Column(
            "success_rate",
            sa.Numeric(5, 2),
            nullable=True,
            comment="成功率（%）",
        ),
        sa.Column(
            "average_task_time_minutes",
            sa.Integer(),
            nullable=True,
            comment="平均タスク処理時間（分）",
        ),
        sa.Column(
            "rating",
            sa.Numeric(3, 2),
            nullable=True,
            comment="評価スコア（5段階）",
        ),
        sa.Column("notes", sa.Text(), nullable=True, comment="管理者用メモ・備考"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # インデックス作成
    op.create_index(
        op.f("ix_workers_user_id"),
        "workers",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_workers_organization_id"),
        "workers",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workers_status"),
        "workers",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """ワーカーテーブルを削除"""
    op.drop_index(op.f("ix_workers_status"), table_name="workers")
    op.drop_index(op.f("ix_workers_organization_id"), table_name="workers")
    op.drop_index(op.f("ix_workers_user_id"), table_name="workers")
    op.drop_table("workers")

    # Enum型を削除
    op.execute("DROP TYPE IF EXISTS skill_level")
    op.execute("DROP TYPE IF EXISTS worker_status")
