"""
ユーザーモデル

全ロール（営業支援会社、顧客、ワーカー）共通のユーザーテーブル。
認証情報を含みます。
"""
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    ユーザーテーブル

    全ロール共通のユーザー情報を管理します。
    organization_idによってマルチテナント分離されます。
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 所属組織（マルチテナントキー）
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属組織ID",
    )

    # 認証情報
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True, comment="メールアドレス（ログインID）"
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="ハッシュ化パスワード")

    # プロフィール情報
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="氏名")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="電話番号")
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="プロフィール画像URL")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="備考")

    # アカウント状態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="アクティブフラグ")
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="メール認証済みフラグ"
    )

    # リレーションシップ
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, organization_id={self.organization_id})>"
