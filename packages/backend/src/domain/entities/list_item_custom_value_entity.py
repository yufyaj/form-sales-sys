"""
リスト項目カスタム値エンティティ

ドメイン層のリスト項目カスタム値モデル。
カスタムカラムの実際の値を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListItemCustomValueEntity:
    """
    リスト項目カスタム値エンティティ

    リスト項目の各カスタムカラムに対する実際の値をビジネスロジックの観点から表現します。
    """

    id: int
    list_item_id: int  # FK to list_items.id
    custom_column_setting_id: int  # FK to custom_column_settings.id
    value: dict | None = None  # カスタムカラムの値（JSONで管理）
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_value(self) -> bool:
        """値が設定されているかを判定"""
        return self.value is not None and bool(self.value)
