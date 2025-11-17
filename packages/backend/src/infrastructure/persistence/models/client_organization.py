"""
顧客組織モデル

顧客企業の詳細情報を管理するテーブル。
Organizationテーブルと1:1の関係を持ちます。
"""
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ClientOrganization(Base, TimestampMixin, SoftDeleteMixin):
    """
    顧客組織テーブル

    顧客企業の詳細情報を管理します。
    Organizationテーブルと1:1の関係を持ち、営業支援会社が管理する顧客情報を格納します。
    """

    __tablename__ = "client_organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Organizationテーブルとの1:1関係
    # RESTRICT: Organizationが削除される前に、ClientOrganizationを削除する必要がある
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="対応するOrganizationのID（1:1関係）",
    )

    # 顧客企業情報
    industry: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="業種"
    )
    employee_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="従業員数"
    )
    annual_revenue: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, comment="年商（円）"
    )
    established_year: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="設立年"
    )
    website: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Webサイト"
    )
    sales_person: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="担当営業"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="備考")

    # リレーションシップ
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="client_organization"
    )
    contacts: Mapped[list["ClientContact"]] = relationship(
        "ClientContact",
        back_populates="client_organization",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="client_organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ClientOrganization(id={self.id}, organization_id={self.organization_id})>"
