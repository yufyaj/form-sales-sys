"""
作業記録モデル

ワーカーがリストアイテムに対して実施したフォーム送信作業の記録を管理するテーブル。
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class WorkRecordStatus(str, PyEnum):
    """作業記録ステータス"""

    SENT = "sent"  # 送信済み
    CANNOT_SEND = "cannot_send"  # 送信不可


class WorkRecord(Base, TimestampMixin, SoftDeleteMixin):
    """
    作業記録テーブル

    ワーカーがリストアイテムに対して実施したフォーム送信作業の記録を管理します。
    送信済み/送信不可のステータス、作業日時、送信結果の詳細を記録します。
    """

    __tablename__ = "work_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 外部キー: リスト項目割り当て
    # CASCADE: 割り当てが削除されたら作業記録も削除
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("list_item_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リスト項目割り当てID",
    )

    # 外部キー: ワーカー
    # CASCADE: ワーカーが削除されたら作業記録も削除
    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ワーカーID",
    )

    # ステータス: 送信済み or 送信不可
    status: Mapped[WorkRecordStatus] = mapped_column(
        Enum(WorkRecordStatus, name="work_record_status", create_constraint=True),
        nullable=False,
        index=True,
        comment="送信済みまたは送信不可",
    )

    # 作業開始日時
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="作業開始日時",
    )

    # 作業完了日時
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="作業完了日時",
    )

    # 送信結果の詳細（JSONフィールド）
    # 送信成功時のレスポンス、エラーメッセージ、スクリーンショットURLなどを格納
    form_submission_result: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="送信結果の詳細（JSONフィールド）",
    )

    # 外部キー: 送信不可理由（送信不可の場合のみ）
    # SET NULL: 理由マスターが削除されてもNULLになるだけで記録は残す
    cannot_send_reason_id: Mapped[int | None] = mapped_column(
        ForeignKey("cannot_send_reasons.id", ondelete="SET NULL"),
        nullable=True,
        comment="送信不可理由ID（送信不可の場合のみ）",
    )

    # メモ・備考
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="メモ・備考",
    )

    # リレーションシップ
    assignment: Mapped["ListItemAssignment"] = relationship(
        "ListItemAssignment",
        back_populates="work_records"
    )
    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="work_records"
    )
    cannot_send_reason: Mapped["CannotSendReason | None"] = relationship(
        "CannotSendReason",
        back_populates="work_records"
    )

    def __repr__(self) -> str:
        return f"<WorkRecord(id={self.id}, worker_id={self.worker_id}, status={self.status})>"
