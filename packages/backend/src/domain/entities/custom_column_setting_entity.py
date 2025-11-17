"""
カスタムカラム設定エンティティ

ドメイン層のカスタムカラム設定モデル。
リストに追加できるカスタムカラムの設定を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CustomColumnSettingEntity:
    """
    カスタムカラム設定エンティティ

    リストごとのカスタムカラム設定をビジネスロジックの観点から表現します。
    カラムの型、検証ルール、オプションなどを柔軟に管理します。
    """

    id: int
    list_id: int  # FK to lists.id
    column_name: str  # カラム識別子（プログラムで使用）
    display_name: str  # カラム表示名（UI用）
    column_config: dict  # カラム設定（型、検証ルール、オプションなど）
    display_order: int  # 表示順序
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_valid_config(self) -> bool:
        """カラム設定が有効かを判定"""
        return bool(
            self.column_config
            and isinstance(self.column_config, dict)
            and "type" in self.column_config
        )
