"""
プロジェクトモデル

顧客組織に紐づくプロジェクト情報を管理するテーブル。
"""
from enum import Enum

from sqlalchemy import BigInteger, CheckConstraint, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ProjectStatus(str, Enum):
    """プロジェクトステータス"""

    PLANNING = "planning"  # 計画中
    ACTIVE = "active"  # 進行中
    PAUSED = "paused"  # 一時停止
    COMPLETED = "completed"  # 完了
    ARCHIVED = "archived"  # アーカイブ


class Project(Base, TimestampMixin, SoftDeleteMixin):
    """
    プロジェクトテーブル

    顧客組織に紐づくプロジェクト情報を管理します。
    各プロジェクトは特定の顧客組織と営業支援組織に属します（マルチテナント対応）。
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # マルチテナント対応: 営業支援組織ID
    # RESTRICT: Organizationが削除される前に、Projectを削除する必要がある
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="営業支援組織ID（マルチテナント用）",
    )

    # 顧客組織との関連
    # RESTRICT: ClientOrganizationが削除される前に、Projectを削除する必要がある
    client_organization_id: Mapped[int] = mapped_column(
        ForeignKey("client_organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="顧客組織ID",
    )

    # プロジェクト基本情報
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="プロジェクト名（最大100文字）"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="プロジェクト説明"
    )
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, name="project_status_enum", create_constraint=True),
        nullable=False,
        default=ProjectStatus.PLANNING,
        server_default=ProjectStatus.PLANNING.value,
        comment="プロジェクトステータス",
    )

    # 進捗情報（集計用カラム）
    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="進捗率（0-100）",
    )
    total_lists: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="総リスト数",
    )
    completed_lists: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="完了リスト数",
    )
    total_submissions: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="総送信数",
    )

    # リレーションシップ
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="projects"
    )
    client_organization: Mapped["ClientOrganization"] = relationship(
        "ClientOrganization", back_populates="projects"
    )

    # テーブル制約
    __table_args__ = (
        # 進捗率は0-100の範囲
        CheckConstraint("progress >= 0 AND progress <= 100", name="check_progress_range"),
        # 総リスト数、完了リスト数は0以上
        CheckConstraint("total_lists >= 0", name="check_total_lists_non_negative"),
        CheckConstraint("completed_lists >= 0", name="check_completed_lists_non_negative"),
        # 完了リスト数は総リスト数以下
        CheckConstraint("completed_lists <= total_lists", name="check_completed_lists_le_total"),
        # 総送信数は0以上
        CheckConstraint("total_submissions >= 0", name="check_total_submissions_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status.value})>"
