"""
プロジェクトエンティティ

ドメイン層のプロジェクトモデル。営業プロジェクトの情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """プロジェクトのステータス"""
    PLANNING = "planning"  # 企画中
    ACTIVE = "active"  # 進行中
    COMPLETED = "completed"  # 完了
    CANCELLED = "cancelled"  # キャンセル


@dataclass
class ProjectEntity:
    """
    プロジェクトエンティティ

    営業プロジェクトの情報をビジネスロジックの観点から表現します。
    顧客組織と営業支援会社の関連を持ちます。
    """

    id: int
    name: str  # プロジェクト名
    client_organization_id: int  # FK to client_organizations.id
    sales_support_organization_id: int  # FK to organizations.id (テナント分離用)
    status: ProjectStatus  # ステータス
    start_date: date | None = None  # 開始日
    end_date: date | None = None  # 終了日
    description: str | None = None  # 説明
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """プロジェクトが進行中かを判定"""
        return self.status == ProjectStatus.ACTIVE and not self.is_deleted()

    def is_completed(self) -> bool:
        """プロジェクトが完了しているかを判定"""
        return self.status == ProjectStatus.COMPLETED

    def can_start(self) -> bool:
        """プロジェクトを開始できるかを判定（企画中のみ開始可能）"""
        return self.status == ProjectStatus.PLANNING and not self.is_deleted()

    def can_complete(self) -> bool:
        """プロジェクトを完了できるかを判定（進行中のみ完了可能）"""
        return self.status == ProjectStatus.ACTIVE and not self.is_deleted()
