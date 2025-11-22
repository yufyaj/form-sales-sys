"""
組織モデル

営業支援会社と顧客企業の両方を表すテーブル。
マルチテナント対応の基盤となります。
"""
from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class OrganizationType(str, PyEnum):
    """組織タイプ"""

    SALES_SUPPORT = "sales_support"  # 営業支援会社
    CLIENT = "client"  # 顧客企業


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    """
    組織テーブル

    営業支援会社と顧客企業の両方を管理します。
    すべてのデータはこのorganization_idによってテナント分離されます。
    """

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="組織名")
    type: Mapped[OrganizationType] = mapped_column(
        Enum(OrganizationType, name="organization_type"),
        nullable=False,
        comment="組織タイプ（営業支援会社/顧客企業）",
    )

    # 営業支援会社の場合はNULL、顧客企業の場合は担当する営業支援会社のID
    # RESTRICT: 親組織が削除される前に、子組織を削除または親組織IDをNULLにする必要がある
    parent_organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="親組織ID（顧客企業の場合、担当する営業支援会社のID）",
    )

    # オプション情報
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="代表メール")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="代表電話番号")
    address: Mapped[str | None] = mapped_column(Text, nullable=True, comment="住所")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="備考")

    # リレーションシップ
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", cascade="all, delete-orphan"
    )
    client_organization: Mapped["ClientOrganization | None"] = relationship(
        "ClientOrganization",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sales_company_staff: Mapped[list["SalesCompanyStaff"]] = relationship(
        "SalesCompanyStaff",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    workers: Mapped[list["Worker"]] = relationship(
        "Worker", back_populates="organization", cascade="all, delete-orphan"
    )
    lists: Mapped[list["List"]] = relationship(
        "List", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, type={self.type})>"
