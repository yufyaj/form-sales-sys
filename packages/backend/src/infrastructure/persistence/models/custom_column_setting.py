"""
カスタムカラム設定モデル

リストに追加できるカスタムカラムの設定を管理するテーブル。
JSONB型でカラムの型、検証ルール、オプションなどを柔軟に管理します。
"""
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class CustomColumnSetting(Base, TimestampMixin, SoftDeleteMixin):
    """
    カスタムカラム設定テーブル

    リストごとのカスタムカラム設定を管理します。
    JSONB型で型定義、検証ルール、オプションなどを柔軟に管理できます。
    """

    __tablename__ = "custom_column_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Listテーブルとの多対1関係
    # CASCADE: Listが削除された場合、関連するCustomColumnSettingも削除される
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リストID",
    )

    # カラム設定
    column_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="カラム識別子（一意な名前、プログラムで使用）",
    )
    display_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="カラム表示名（UI用）"
    )
    column_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="カラム設定（型、検証ルール、オプションなどをJSONで管理）",
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="表示順序"
    )

    # リレーションシップ
    list: Mapped["List"] = relationship(
        "List", back_populates="custom_column_settings"
    )
    list_item_custom_values: Mapped[list["ListItemCustomValue"]] = relationship(
        "ListItemCustomValue",
        back_populates="custom_column_setting",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "list_id",
            "column_name",
            name="uq_custom_column_settings_list_id_column_name",
        ),
    )

    def __repr__(self) -> str:
        return f"<CustomColumnSetting(id={self.id}, list_id={self.list_id}, column_name={self.column_name})>"
