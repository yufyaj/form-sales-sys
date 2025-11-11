"""
顧客組織エンティティ

ドメイン層の顧客組織モデル。顧客企業の詳細情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClientOrganizationEntity:
    """
    顧客組織エンティティ

    顧客企業の詳細情報をビジネスロジックの観点から表現します。
    Organizationテーブルと1:1の関係を持ちます。
    """

    id: int
    organization_id: int  # FK to organizations.id
    industry: str | None = None  # 業種
    employee_count: int | None = None  # 従業員数
    annual_revenue: int | None = None  # 年商（円）
    established_year: int | None = None  # 設立年
    website: str | None = None  # Webサイト
    sales_person: str | None = None  # 担当営業
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
                self.industry,
                self.employee_count is not None,
                self.annual_revenue is not None,
            ]
        )
