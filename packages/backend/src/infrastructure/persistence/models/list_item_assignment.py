"""
リスト項目割り当てモデル

ワーカーとリスト項目の多対多リレーションを管理する中間テーブル。
重複割り当て防止のための複合ユニーク制約を持ちます。
"""
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class ListItemAssignment(Base, TimestampMixin):
    """
    リスト項目割り当てテーブル

    リスト項目にワーカーを割り当てる多対多リレーションを管理します。
    同じワーカーを同じリスト項目に複数回割り当てることはできません。
    """

    __tablename__ = "list_item_assignments"

    # プライマリキー
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # 外部キー
    # CASCADE: リスト項目が削除された場合、割り当ても削除される
    list_item_id: Mapped[int] = mapped_column(
        ForeignKey("list_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リスト項目ID"
    )

    # CASCADE: ワーカーが削除された場合、割り当ても削除される
    # （ただし、Workerテーブルは論理削除を使用しているため、実際には物理削除されない）
    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ワーカーID"
    )

    # リレーションシップ（双方向）
    list_item: Mapped["ListItem"] = relationship(
        "ListItem",
        back_populates="list_item_assignments"
    )

    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="list_item_assignments"
    )

    # テーブル制約
    # 重複割り当て防止: 同じリスト項目に同じワーカーを複数回割り当てできない
    __table_args__ = (
        UniqueConstraint("list_item_id", "worker_id", name="uq_list_item_worker"),
    )

    def __repr__(self) -> str:
        return (
            f"<ListItemAssignment(id={self.id}, "
            f"list_item_id={self.list_item_id}, worker_id={self.worker_id})>"
        )
