"""
送信不可理由モデル

フォーム送信が不可能な理由のマスターデータを管理するテーブル。
"""
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class CannotSendReason(Base, TimestampMixin, SoftDeleteMixin):
    """
    送信不可理由テーブル

    フォーム送信が不可能な理由のマスターデータを管理します。
    work_recordsテーブルから参照されます。
    """

    __tablename__ = "cannot_send_reasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED, INVALID_EMAIL等）
    reason_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）",
    )

    # 理由名（日本語での表示名）
    reason_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="理由名",
    )

    # 詳細説明
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="詳細説明",
    )

    # 有効/無効フラグ
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="有効/無効フラグ",
    )

    # リレーションシップ
    work_records: Mapped[list["WorkRecord"]] = relationship(
        "WorkRecord",
        back_populates="cannot_send_reason"
    )

    def __repr__(self) -> str:
        return f"<CannotSendReason(id={self.id}, reason_code={self.reason_code}, reason_name={self.reason_name})>"
