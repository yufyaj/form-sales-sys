"""
ワーカーモデル

フォーム営業の実務作業者情報を管理するテーブル。
Userテーブルと1:1の関係を持ちます。
"""
from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class WorkerStatus(str, PyEnum):
    """ワーカーステータス"""

    PENDING = "pending"  # 承認待ち
    ACTIVE = "active"  # 稼働中
    INACTIVE = "inactive"  # 休止中
    SUSPENDED = "suspended"  # 停止中


class SkillLevel(str, PyEnum):
    """スキルレベル"""

    BEGINNER = "beginner"  # 初級
    INTERMEDIATE = "intermediate"  # 中級
    ADVANCED = "advanced"  # 上級
    EXPERT = "expert"  # エキスパート


class Worker(Base, TimestampMixin, SoftDeleteMixin):
    """
    ワーカーテーブル

    フォーム営業の実務作業者情報を管理します。
    Userテーブルと1:1の関係を持ち、ワーカー固有の情報を格納します。
    """

    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Userテーブルとの1:1関係
    # RESTRICT: Userが削除される前にWorkerを削除する必要がある
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="対応するUserのID（1:1関係）",
    )

    # 所属組織（マルチテナントキー）
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属組織ID（営業支援会社）",
    )

    # ワーカー基本情報
    status: Mapped[WorkerStatus] = mapped_column(
        Enum(WorkerStatus, name="worker_status", create_constraint=True),
        nullable=False,
        default=WorkerStatus.PENDING,
        index=True,
        comment="ワーカーステータス",
    )

    # スキル・経験情報
    skill_level: Mapped[SkillLevel | None] = mapped_column(
        Enum(SkillLevel, name="skill_level"),
        nullable=True,
        comment="スキルレベル",
    )

    experience_months: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="経験月数",
    )

    specialties: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="得意分野・専門領域（JSON配列またはカンマ区切り）",
    )

    # 稼働情報
    max_tasks_per_day: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="1日の最大タスク数",
    )

    available_hours_per_week: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="週間稼働可能時間",
    )

    # パフォーマンス指標
    completed_tasks_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="完了タスク数",
    )

    success_rate: Mapped[float | None] = mapped_column(
        Numeric(5, 2),  # 0.00 ~ 100.00
        nullable=True,
        comment="成功率（%）",
    )

    average_task_time_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="平均タスク処理時間（分）",
    )

    # 評価情報
    rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),  # 0.00 ~ 5.00
        nullable=True,
        comment="評価スコア（5段階）",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="管理者用メモ・備考",
    )

    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="worker")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="workers")
    list_item_assignments: Mapped[list["ListItemAssignment"]] = relationship(
        "ListItemAssignment",
        back_populates="worker"
    )
    work_records: Mapped[list["WorkRecord"]] = relationship(
        "WorkRecord",
        back_populates="worker"
    )
    questions: Mapped[list["WorkerQuestion"]] = relationship(
        "WorkerQuestion",
        back_populates="worker",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Worker(id={self.id}, user_id={self.user_id}, status={self.status})>"
