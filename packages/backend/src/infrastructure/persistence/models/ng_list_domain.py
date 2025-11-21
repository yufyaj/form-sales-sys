"""
NGリストドメインモデル

リストごとのNG（送信禁止）ドメインを管理するテーブル。
"""
from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class NgListDomain(Base, TimestampMixin, SoftDeleteMixin):
    """
    NGリストドメインテーブル

    リストごとのNG（送信禁止）ドメインを管理します。
    各NGドメインは特定のリストに紐付きます。
    """

    __tablename__ = "ng_list_domains"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Listテーブルとの多対1関係
    # CASCADE: Listが削除された場合、関連するNgListDomainも削除される
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="リストID（FK to lists.id）",
    )

    # ドメイン情報
    domain: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="元のドメインパターン（ユーザー入力）"
    )
    domain_pattern: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="正規化されたドメインパターン（比較用）",
    )
    is_wildcard: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False, comment="ワイルドカード使用フラグ"
    )
    memo: Mapped[str | None] = mapped_column(Text, nullable=True, comment="メモ（任意）")

    # リレーションシップ
    list: Mapped["List"] = relationship("List", back_populates="ng_domains")

    # 制約: 同一リスト内でのドメインパターンの重複を防ぐ
    __table_args__ = (
        UniqueConstraint(
            "list_id",
            "domain_pattern",
            name="uq_ng_list_domains_list_id_domain_pattern",
        ),
    )

    def __repr__(self) -> str:
        return f"<NgListDomain(id={self.id}, list_id={self.list_id}, domain_pattern={self.domain_pattern})>"
