"""
ユーザー・ロール関連モデル

ユーザーとロールの多対多リレーションを管理します。
"""
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class UserRole(Base, TimestampMixin):
    """
    ユーザー・ロール中間テーブル

    ユーザーに割り当てられたロールを管理します。
    一人のユーザーが複数のロールを持つことができます。
    """

    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="ユーザーID"
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True, comment="ロールID"
    )

    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class RolePermission(Base, TimestampMixin):
    """
    ロール・権限中間テーブル

    ロールに割り当てられた権限を管理します。
    """

    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True, comment="ロールID"
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="権限ID",
    )

    # リレーションシップ
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
