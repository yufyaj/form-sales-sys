"""
リスト項目モデル

リストに含まれる営業先企業情報を管理するテーブル。
各項目はカスタムカラムの値を持つことができます。
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ListItem(Base, TimestampMixin, SoftDeleteMixin):
    """
    リスト項目テーブル

    リストに含まれる営業先企業情報を管理します。
    各項目はカスタムカラムの値を保持できます。
    """

    __tablename__ = "list_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Listテーブルとの多対1関係
    # CASCADE: Listが削除された場合、関連するListItemも削除される
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リストID",
    )

    # リスト項目情報
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="企業名などのタイトル"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="pending",
        comment="ステータス（pending, contacted, negotiatingなど）",
    )

    # リレーションシップ
    list: Mapped["List"] = relationship("List", back_populates="list_items")
    custom_values: Mapped[list["ListItemCustomValue"]] = relationship(
        "ListItemCustomValue",
        back_populates="list_item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ListItem(id={self.id}, list_id={self.list_id}, title={self.title})>"
