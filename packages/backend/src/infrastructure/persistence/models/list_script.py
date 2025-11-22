"""
スクリプトモデル

リストごとの営業トーク台本（スクリプト）を管理するテーブル。
各スクリプトはリスト（List）に紐付きます。
"""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ListScript(Base, TimestampMixin, SoftDeleteMixin):
    """
    スクリプトテーブル

    リストごとの営業トーク台本を管理します。
    各スクリプトはリスト（List）に紐付きます。
    """

    __tablename__ = "list_scripts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Listテーブルとの多対1関係
    # CASCADE: Listが削除された場合、関連するListScriptも削除される
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リストID（外部キー）",
    )

    # スクリプト情報
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="スクリプトタイトル"
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="スクリプト本文（営業トークの台本）"
    )

    # リレーションシップ
    list: Mapped["List"] = relationship("List", back_populates="scripts")

    def __repr__(self) -> str:
        return f"<ListScript(id={self.id}, title={self.title}, list_id={self.list_id})>"
