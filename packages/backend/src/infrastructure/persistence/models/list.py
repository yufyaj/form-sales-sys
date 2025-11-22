"""
リストモデル

営業先企業リストを管理するテーブル。
プロジェクト（営業支援会社）に紐付きます。
"""
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.list_entity import ListStatus

from .base import Base, SoftDeleteMixin, TimestampMixin


class List(Base, TimestampMixin, SoftDeleteMixin):
    """
    リストテーブル

    営業先企業リストを管理します。
    各リストは営業支援会社（Organization）に紐付きます。
    """

    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Organizationテーブルとの多対1関係
    # CASCADE: Organizationが削除された場合、関連するListも削除される
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="営業支援会社のID（マルチテナント対応）",
    )

    # リスト情報
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="リスト名"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="リストの説明"
    )
    status: Mapped[ListStatus] = mapped_column(
        SQLAlchemyEnum(ListStatus),
        nullable=False,
        default=ListStatus.DRAFT,
        server_default="draft",
        comment="リストステータス(draft/submitted/accepted/rejected)",
    )

    # リレーションシップ
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="lists"
    )
    list_items: Mapped[list["ListItem"]] = relationship(
        "ListItem",
        back_populates="list",
        cascade="all, delete-orphan",
    )
    custom_column_settings: Mapped[list["CustomColumnSetting"]] = relationship(
        "CustomColumnSetting",
        back_populates="list",
        cascade="all, delete-orphan",
    )
    ng_domains: Mapped[list["NgListDomain"]] = relationship(
        "NgListDomain",
        back_populates="list",
        cascade="all, delete-orphan",
    )
    no_send_settings: Mapped[list["NoSendSetting"]] = relationship(
        "NoSendSetting",
        back_populates="list",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<List(id={self.id}, name={self.name}, organization_id={self.organization_id})>"
