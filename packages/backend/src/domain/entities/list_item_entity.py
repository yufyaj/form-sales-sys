"""
リスト項目エンティティ

ドメイン層のリスト項目モデル。営業先企業情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListItemEntity:
    """
    リスト項目エンティティ

    リストに含まれる営業先企業情報をビジネスロジックの観点から表現します。
    各項目はカスタムカラムの値を保持できます。
    """

    id: int
    list_id: int  # FK to lists.id
    title: str  # 企業名などのタイトル
    status: str  # ステータス（pending, contacted, negotiatingなど）
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_title(self) -> bool:
        """タイトルが設定されているかを判定"""
        return bool(self.title and self.title.strip())

    def is_pending(self) -> bool:
        """ステータスがpendingかを判定"""
        return self.status == "pending"

    def is_contacted(self) -> bool:
        """ステータスがcontactedかを判定"""
        return self.status == "contacted"
