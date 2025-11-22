"""
リストエンティティ

ドメイン層のリストモデル。営業先企業リストを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ListStatus(str, Enum):
    """
    リストステータス列挙型

    リストの検収状態を表現します。
    """

    DRAFT = "draft"  # 下書き: 作成中、編集可能
    SUBMITTED = "submitted"  # 提出済み: 検収待ち
    ACCEPTED = "accepted"  # 検収済み: 編集不可
    REJECTED = "rejected"  # 差し戻し: 再編集可能


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
    status: ListStatus = ListStatus.DRAFT  # リストステータス
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_name(self) -> bool:
        """リスト名が設定されているかを判定"""
        return bool(self.name and self.name.strip())

    def is_editable(self) -> bool:
        """
        編集可能かを判定

        検収済み(accepted)の場合は編集不可
        それ以外のステータス(draft, submitted, rejected)は編集可能
        """
        return self.status != ListStatus.ACCEPTED

    def can_submit(self) -> bool:
        """
        提出可能かを判定

        下書き(draft)または差し戻し(rejected)の場合のみ提出可能
        """
        return self.status in (ListStatus.DRAFT, ListStatus.REJECTED)

    def can_accept(self) -> bool:
        """
        検収可能かを判定

        提出済み(submitted)の場合のみ検収可能
        """
        return self.status == ListStatus.SUBMITTED

    def can_reject(self) -> bool:
        """
        差し戻し可能かを判定

        提出済み(submitted)の場合のみ差し戻し可能
        """
        return self.status == ListStatus.SUBMITTED
