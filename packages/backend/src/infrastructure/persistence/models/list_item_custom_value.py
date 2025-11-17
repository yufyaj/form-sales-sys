"""
リスト項目カスタム値モデル

リスト項目の各カスタムカラムに対する実際の値を管理するテーブル。
JSONB型で柔軟に値を保存します。
"""
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ListItemCustomValue(Base, TimestampMixin, SoftDeleteMixin):
    """
    リスト項目カスタム値テーブル

    リスト項目の各カスタムカラムに対する実際の値を管理します。
    JSONB型で値を保存し、柔軟なデータ型に対応します。
    """

    __tablename__ = "list_item_custom_values"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ListItemテーブルとの多対1関係
    # CASCADE: ListItemが削除された場合、関連するListItemCustomValueも削除される
    list_item_id: Mapped[int] = mapped_column(
        ForeignKey("list_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リスト項目ID",
    )

    # CustomColumnSettingテーブルとの多対1関係
    # CASCADE: CustomColumnSettingが削除された場合、関連するListItemCustomValueも削除される
    custom_column_setting_id: Mapped[int] = mapped_column(
        ForeignKey("custom_column_settings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="カスタムカラム設定ID",
    )

    # カスタムカラムの実際の値
    value: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="カスタムカラムの値（文字列、数値、真偽値、配列などをJSONで管理）",
    )

    # リレーションシップ
    list_item: Mapped["ListItem"] = relationship(
        "ListItem", back_populates="custom_values"
    )
    custom_column_setting: Mapped["CustomColumnSetting"] = relationship(
        "CustomColumnSetting", back_populates="list_item_custom_values"
    )

    __table_args__ = (
        UniqueConstraint(
            "list_item_id",
            "custom_column_setting_id",
            name="uq_list_item_custom_val_item_setting",
        ),
    )

    def __repr__(self) -> str:
        return f"<ListItemCustomValue(id={self.id}, list_item_id={self.list_item_id}, custom_column_setting_id={self.custom_column_setting_id})>"
