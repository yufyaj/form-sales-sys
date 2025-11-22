"""
リスト項目割り当てエンティティ

ドメイン層のリスト項目割り当てモデル。
リスト項目とワーカーの多対多リレーションを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListItemAssignmentEntity:
    """
    リスト項目割り当てエンティティ

    リスト項目にワーカーを割り当てる多対多リレーションをビジネスロジックの観点から表現します。
    重複割り当ては、データベースの複合ユニーク制約で防止されます。
    """

    id: int
    list_item_id: int  # FK to list_items.id
    worker_id: int  # FK to workers.id
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_assigned_to_worker(self, worker_id: int) -> bool:
        """指定されたワーカーに割り当てられているかを判定"""
        return self.worker_id == worker_id

    def is_assigned_to_list_item(self, list_item_id: int) -> bool:
        """指定されたリスト項目に割り当てられているかを判定"""
        return self.list_item_id == list_item_id
