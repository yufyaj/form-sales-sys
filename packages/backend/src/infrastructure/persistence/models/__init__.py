"""
データベースモデル

SQLAlchemy 2.0を使用したデータベースモデルを提供します。
マルチテナント対応の設計となっています。
"""
from .base import Base, SoftDeleteMixin, TimestampMixin
from .client_contact import ClientContact
from .client_organization import ClientOrganization
from .custom_column_setting import CustomColumnSetting
from .list import List
from .list_item import ListItem
from .list_item_custom_value import ListItemCustomValue
from .list_script import ListScript
from .ng_list_domain import NgListDomain
from .no_send_setting import NoSendSetting
from .organization import Organization, OrganizationType
from .project import Project, ProjectPriority, ProjectStatus
from .role import Permission, Role
from .sales_company_staff import SalesCompanyStaff
from .user import User
from .user_role import RolePermission, UserRole
from .worker import SkillLevel, Worker, WorkerStatus

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
    "SalesCompanyStaff",
    "Worker",
    "WorkerStatus",
    "SkillLevel",
    "Project",
    "ProjectStatus",
    "ProjectPriority",
    # Phase3: List Management
    "List",
    "CustomColumnSetting",
    "ListItem",
    "ListItemCustomValue",
    "ListScript",
    "NgListDomain",
    "NoSendSetting",
]
