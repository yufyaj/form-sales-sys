"""
プロジェクトモデル

顧客組織に紐づくプロジェクト情報を管理するテーブル。
"""
from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ProjectStatus(str, PyEnum):
    """プロジェクトステータス"""

    PLANNING = "planning"  # 企画中
    IN_PROGRESS = "in_progress"  # 進行中
    ON_HOLD = "on_hold"  # 保留
    COMPLETED = "completed"  # 完了
    CANCELLED = "cancelled"  # キャンセル


class ProjectPriority(str, PyEnum):
    """プロジェクト優先度"""

    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    CRITICAL = "critical"  # 緊急


class Project(Base, TimestampMixin, SoftDeleteMixin):
    """
    プロジェクトテーブル

    顧客組織に紐づくプロジェクト情報を管理します。
    """

    __tablename__ = "projects"

    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 顧客組織との紐付け（必須）
    # RESTRICT: プロジェクトが存在する顧客組織は削除できない
    client_organization_id: Mapped[int] = mapped_column(
        ForeignKey("client_organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="顧客組織ID",
    )

    # 基本情報（必須）
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="プロジェクト名",
    )

    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.PLANNING,
        index=True,  # ステータスでのフィルタリングが頻繁
        comment="プロジェクトステータス",
    )

    # 基本情報（オプション）
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="プロジェクト説明",
    )

    # スケジュール情報
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="開始予定日",
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="終了予定日",
    )

    # 予算情報
    estimated_budget: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="見積予算（円）",
    )

    actual_budget: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="実績予算（円）",
    )

    # 優先度
    priority: Mapped[ProjectPriority | None] = mapped_column(
        Enum(ProjectPriority, name="project_priority"),
        nullable=True,
        default=ProjectPriority.MEDIUM,
        comment="プロジェクト優先度",
    )

    # プロジェクトオーナー（担当者）
    # SET NULL: ユーザーが削除されてもプロジェクトは残す
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="プロジェクトオーナー（担当ユーザー）",
    )

    # 備考
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="備考",
    )

    # リレーションシップ
    client_organization: Mapped["ClientOrganization"] = relationship(
        "ClientOrganization",
        back_populates="projects",
    )

    owner: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[owner_user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Project(id={self.id}, name={self.name}, "
            f"client_organization_id={self.client_organization_id}, "
            f"status={self.status})>"
        )
