"""
営業支援会社担当者モデル

営業支援会社の自社担当者情報を管理するテーブル。
Userテーブルと1:1の関係を持ちます。
"""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class SalesCompanyStaff(Base, TimestampMixin, SoftDeleteMixin):
    """
    営業支援会社担当者テーブル

    営業支援会社の自社担当者情報を管理します。
    Userテーブルと1:1の関係を持ち、営業支援会社固有の担当者情報を格納します。
    """

    __tablename__ = "sales_company_staff"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Userテーブルとの1:1関係
    # RESTRICT: Userが削除される前に、SalesCompanyStaffを削除する必要がある
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="対応するUserのID（1:1関係）",
    )

    # 営業支援会社の組織ID（マルチテナントキー）
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="営業支援会社の組織ID",
    )

    # 営業支援会社担当者情報
    department: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="部署"
    )
    position: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="役職"
    )
    employee_number: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="社員番号"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="備考")

    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="sales_company_staff")
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="sales_company_staff"
    )

    def __repr__(self) -> str:
        return f"<SalesCompanyStaff(id={self.id}, user_id={self.user_id}, organization_id={self.organization_id})>"
