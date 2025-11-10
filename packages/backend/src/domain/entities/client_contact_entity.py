"""
顧客担当者エンティティ

ドメイン層の顧客担当者モデル。顧客企業内の担当者情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClientContactEntity:
    """
    顧客担当者エンティティ

    顧客企業内の担当者をビジネスロジックの観点から表現します。
    1つの顧客組織（ClientOrganization）に複数の担当者が紐づきます。
    """

    id: int
    client_organization_id: int  # FK to client_organizations.id
    full_name: str  # 氏名
    department: str | None = None  # 部署
    position: str | None = None  # 役職
    email: str | None = None  # メールアドレス
    phone: str | None = None  # 電話番号
    mobile: str | None = None  # 携帯電話番号
    is_primary: bool = False  # 主担当フラグ
    notes: str | None = None  # 備考
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_contact_info(self) -> bool:
        """連絡先情報が設定されているかを判定"""
        return bool(self.email or self.phone or self.mobile)

    def get_display_name(self) -> str:
        """表示用の名前を取得（役職付き）"""
        if self.position:
            return f"{self.full_name}（{self.position}）"
        return self.full_name
