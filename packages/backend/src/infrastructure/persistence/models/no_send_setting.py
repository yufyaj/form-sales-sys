"""
送信禁止設定モデル

営業メール等の自動送信を禁止する時間帯・曜日・日付を管理するテーブル。
リストに紐付きます。
"""
from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class NoSendSetting(Base, TimestampMixin, SoftDeleteMixin):
    """
    送信禁止設定テーブル

    営業メール等の自動送信を禁止する時間帯・曜日・日付を管理します。
    各設定はリストに紐付きます。
    """

    __tablename__ = "no_send_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Listテーブルとの多対1関係
    # CASCADE: Listが削除された場合、関連するNoSendSettingも削除される
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リストID",
    )

    # 設定種別
    setting_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="設定種別 (day_of_week/time_range/specific_date)",
    )

    # 設定情報
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="設定名（例: 休日設定、夜間送信禁止）"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="設定の説明"
    )

    # 有効/無効フラグ
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
        nullable=False,
        comment="設定の有効/無効",
    )

    # 曜日設定（setting_type=day_of_weekの場合に使用）
    # PostgreSQLのINTEGER配列を使用（ISO 8601準拠: 1=月曜, 7=日曜）
    day_of_week_list: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer),
        nullable=True,
        comment="送信禁止曜日リスト [1=月,2=火,...,7=日]",
    )

    # 時間帯設定（setting_type=time_rangeの場合に使用）
    # PostgreSQLのTIME型を使用（ISO 8601: HH:MM:SS形式）
    time_start: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
        comment="送信禁止開始時刻 (例: 22:00:00)",
    )

    time_end: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
        comment="送信禁止終了時刻 (例: 08:00:00)",
    )

    # 日付設定（setting_type=specific_dateの場合に使用）
    specific_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="送信禁止日 (例: 2025-01-01)",
    )

    # 日付範囲設定（連続した複数日の禁止期間）
    date_range_start: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="送信禁止期間開始日 (例: 2025-12-29)",
    )

    date_range_end: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="送信禁止期間終了日 (例: 2026-01-03)",
    )

    # リレーションシップ
    list: Mapped["List"] = relationship("List", back_populates="no_send_settings")

    def __repr__(self) -> str:
        return f"<NoSendSetting(id={self.id}, type={self.setting_type}, list_id={self.list_id})>"
