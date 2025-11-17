"""
リストエンティティ

ドメイン層のリストモデル。営業先企業リストを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListEntity:
    """
    リストエンティティ

    営業先企業リストをビジネスロジックの観点から表現します。
    各リストは営業支援会社（Organization）に紐付きます。
    """

    id: int
    organization_id: int  # FK to organizations.id（マルチテナント対応）
    name: str  # リスト名
    description: str | None = None  # リストの説明
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_name(self) -> bool:
        """リスト名が設定されているかを判定"""
        return bool(self.name and self.name.strip())
