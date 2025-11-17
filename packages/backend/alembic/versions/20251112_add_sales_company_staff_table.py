"""add sales_company_staff table

Revision ID: 20251112_0001
Revises: 0d9ad76f670b
Create Date: 2025-11-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251112_0001"
down_revision: Union[str, None] = "0d9ad76f670b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """営業支援会社担当者テーブルを作成"""
    op.create_table(
        "sales_company_staff",
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
            comment="営業支援会社の組織ID",
        ),
        sa.Column("department", sa.String(length=255), nullable=True, comment="部署"),
        sa.Column("position", sa.String(length=255), nullable=True, comment="役職"),
        sa.Column(
            "employee_number", sa.String(length=100), nullable=True, comment="社員番号"
        ),
        sa.Column("notes", sa.Text(), nullable=True, comment="備考"),
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
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sales_company_staff_user_id"),
        "sales_company_staff",
        ["user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_sales_company_staff_organization_id"),
        "sales_company_staff",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    """営業支援会社担当者テーブルを削除"""
    op.drop_index(
        op.f("ix_sales_company_staff_organization_id"), table_name="sales_company_staff"
    )
    op.drop_index(op.f("ix_sales_company_staff_user_id"), table_name="sales_company_staff")
    op.drop_table("sales_company_staff")
