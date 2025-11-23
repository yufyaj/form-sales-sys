"""
ワーカー質問モデル

ワーカーが営業支援会社に対して行う質問を管理するテーブル。
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class QuestionStatus(str, PyEnum):
    """質問ステータス"""

    PENDING = "pending"  # 未対応
    IN_REVIEW = "in_review"  # 確認中
    ANSWERED = "answered"  # 回答済み
    CLOSED = "closed"  # クローズ済み


class QuestionPriority(str, PyEnum):
    """質問優先度"""

    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 緊急


class WorkerQuestion(Base, TimestampMixin, SoftDeleteMixin):
    """
    ワーカー質問テーブル

    ワーカーが営業支援会社に対して行う質問を管理します。
    マルチテナント対応のため、organization_idでテナント分離を行います。
    """

    __tablename__ = "worker_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ワーカー（質問者）
    # RESTRICT: Workerが削除される前にWorkerQuestionを削除する必要がある
    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="質問者のワーカーID",
    )

    # 所属組織（マルチテナントキー）
    # CASCADE: 営業支援会社が削除されたら、その配下の質問も削除する
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="営業支援会社の組織ID（マルチテナントキー）",
    )

    # 顧客組織（オプション）
    # SET NULL: 顧客組織が削除されても質問は残す
    client_organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("client_organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="関連する顧客組織ID（オプション）",
    )

    # 質問内容
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="質問タイトル",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="質問内容",
    )

    # ステータス管理
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, name="question_status", create_constraint=True),
        nullable=False,
        default=QuestionStatus.PENDING,
        index=True,
        comment="質問ステータス",
    )

    priority: Mapped[QuestionPriority] = mapped_column(
        Enum(QuestionPriority, name="question_priority", create_constraint=True),
        nullable=False,
        default=QuestionPriority.MEDIUM,
        comment="質問優先度",
    )

    # 回答情報
    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="回答内容",
    )

    # 回答者（営業支援会社のスタッフ）
    # SET NULL: 回答者が削除されても質問と回答は残す
    answered_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="回答者のユーザーID",
    )

    answered_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        comment="回答日時",
    )

    # メタデータ
    tags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="タグ（JSON配列形式）",
    )

    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="営業支援会社用の内部メモ",
    )

    # リレーションシップ
    worker: Mapped["Worker"] = relationship("Worker", back_populates="questions")
    organization: Mapped["Organization"] = relationship("Organization")
    client_organization: Mapped["ClientOrganization | None"] = relationship(
        "ClientOrganization"
    )
    answered_by_user: Mapped["User | None"] = relationship("User")

    # 複合インデックス（パフォーマンス最適化）
    __table_args__ = (
        # 営業支援会社スタッフが未読質問を高速取得するため
        Index(
            "ix_worker_questions_org_status",
            "organization_id",
            "status",
        ),
        # ワーカーの質問履歴を時系列表示するため
        Index(
            "ix_worker_questions_worker_created",
            "worker_id",
            "created_at",
        ),
        # 顧客企業別の質問フィルタリングのため
        Index(
            "ix_worker_questions_client_org_status",
            "client_organization_id",
            "status",
        ),
    )

    def __repr__(self) -> str:
        return f"<WorkerQuestion(id={self.id}, worker_id={self.worker_id}, status={self.status})>"
