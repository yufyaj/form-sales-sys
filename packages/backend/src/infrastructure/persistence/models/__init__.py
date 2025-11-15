"""
データベースモデル

SQLAlchemy 2.0を使用したデータベースモデルを提供します。
マルチテナント対応の設計となっています。
"""
from .base import Base, SoftDeleteMixin, TimestampMixin
from .client_contact import ClientContact
from .client_organization import ClientOrganization
from .organization import Organization, OrganizationType
from .project import Project, ProjectStatus
from .role import Permission, Role
from .user import User
from .user_role import RolePermission, UserRole

__all__ = [
    # Base classes
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    # Models
    "Organization",
    "OrganizationType",
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "ClientOrganization",
    "ClientContact",
    "Project",
    "ProjectStatus",
]
