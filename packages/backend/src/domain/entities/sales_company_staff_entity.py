"""
営業支援会社担当者エンティティ

ドメイン層の営業支援会社担当者モデル。営業支援会社の自社担当者情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SalesCompanyStaffEntity:
    """
    営業支援会社担当者エンティティ

    営業支援会社の自社担当者情報をビジネスロジックの観点から表現します。
    Userテーブルと1:1の関係を持ち、営業支援会社固有の担当者情報を管理します。
    """

    id: int
    user_id: int  # FK to users.id (1:1)
    organization_id: int  # FK to organizations.id (営業支援会社)
    department: str | None = None  # 部署
    position: str | None = None  # 役職
    employee_number: str | None = None  # 社員番号
    notes: str | None = None  # 備考
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_complete_info(self) -> bool:
        """基本情報が揃っているかを判定"""
        return all(
            [
                self.department,
                self.position,
                self.employee_number,
            ]
        )
