"""
顧客担当者モデル

顧客企業内の担当者情報を管理するテーブル。
ClientOrganizationテーブルと多対1の関係を持ちます。
"""
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class ClientContact(Base, TimestampMixin, SoftDeleteMixin):
    """
    顧客担当者テーブル

    顧客企業内の担当者情報を管理します。
    1つの顧客組織（ClientOrganization）に複数の担当者が紐づきます。
    """

    __tablename__ = "client_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ClientOrganizationテーブルとの多対1関係
    # CASCADE: ClientOrganizationが削除されたら、関連するClientContactも削除される
    client_organization_id: Mapped[int] = mapped_column(
        ForeignKey("client_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="顧客組織ID",
    )

    # 担当者情報
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="氏名")
    department: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="部署"
    )
    position: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="役職"
    )
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="メールアドレス"
    )
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="電話番号"
    )
    mobile: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="携帯電話番号"
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="主担当フラグ"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="備考")

    # リレーションシップ
    client_organization: Mapped["ClientOrganization"] = relationship(
        "ClientOrganization", back_populates="contacts"
    )

    def __repr__(self) -> str:
        return f"<ClientContact(id={self.id}, full_name={self.full_name}, is_primary={self.is_primary})>"
