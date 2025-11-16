"""
プロジェクトモデル

営業プロジェクトの情報を管理するテーブル。
顧客組織と営業支援会社の関係を持ちます。
"""
from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class Project(Base, TimestampMixin, SoftDeleteMixin):
    """
    プロジェクトテーブル

    営業プロジェクトの情報を管理します。
    顧客組織との関係を持ち、営業支援会社がプロジェクトを管理します。
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # プロジェクト基本情報
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="プロジェクト名"
    )

    # 顧客組織との関係
    # RESTRICT: ClientOrganizationが削除される前に、Projectを削除する必要がある
    client_organization_id: Mapped[int] = mapped_column(
        ForeignKey("client_organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="顧客組織ID",
    )

    # 営業支援会社との関係（マルチテナント分離用）
    # RESTRICT: Organizationが削除される前に、Projectを削除する必要がある
    sales_support_organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="営業支援会社組織ID（テナント分離用）",
    )

    # プロジェクトステータス
    # planning: 企画中, active: 進行中, completed: 完了, cancelled: キャンセル
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="ステータス: planning, active, completed, cancelled",
    )

    # プロジェクト期間
    start_date: Mapped[Date | None] = mapped_column(
        Date, nullable=True, comment="開始日"
    )
    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True, comment="終了日")

    # プロジェクト詳細
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="説明")

    # リレーションシップ
    client_organization: Mapped["ClientOrganization"] = relationship(
        "ClientOrganization", back_populates="projects"
    )
    sales_support_organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="projects", foreign_keys=[sales_support_organization_id]
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
