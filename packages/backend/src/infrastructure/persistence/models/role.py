"""
ロールモデル

営業支援会社、顧客、ワーカーの3つの基本ロールと権限を管理します。
"""
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    """
    ロールテーブル

    システム全体で使用されるロールを定義します。
    基本的には以下の3つのロールが登録されます：
    - sales_support: 営業支援会社
    - client: 顧客
    - worker: ワーカー
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="ロール名（一意）"
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="表示名")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="説明")

    # リレーションシップ
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(Base, TimestampMixin):
    """
    権限テーブル

    システムで定義される具体的な権限を管理します。
    例: project:create, project:read, project:update, project:delete
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="リソース名（例: project, list, worker）"
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="アクション名（例: create, read, update, delete）"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="説明")

    # リレーションシップ
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permission_resource_action"),
    )

    @property
    def code(self) -> str:
        """権限コード（resource:action形式）"""
        return f"{self.resource}:{self.action}"

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code={self.code})>"
