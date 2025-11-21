"""
NGリストドメインエンティティ

ドメイン層のNGリストドメインモデル。リストごとのNG（送信禁止）ドメインを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NgListDomainEntity:
    """
    NGリストドメインエンティティ

    リストごとに設定されるNG（送信禁止）ドメインをビジネスロジックの観点から表現します。
    各NGドメインは特定のリストに紐付きます。
    """

    id: int
    list_id: int  # FK to lists.id
    domain: str  # 元のドメインパターン（ユーザー入力）
    domain_pattern: str  # 正規化されたドメインパターン（比較用）
    is_wildcard: bool = False  # ワイルドカード使用フラグ
    memo: str | None = None  # メモ（任意）
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_memo(self) -> bool:
        """メモが設定されているかを判定"""
        return bool(self.memo and self.memo.strip())

    def is_wildcard_pattern(self) -> bool:
        """ワイルドカードパターンかを判定"""
        return self.is_wildcard or '*' in self.domain_pattern
