"""
ワーカー質問エンティティ

ドメイン層のワーカー質問モデル。ビジネスロジックの中核を担います。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkerQuestionEntity:
    """
    ワーカー質問エンティティ

    ワーカーが営業支援会社に対して行う質問を表現します。
    データベースの実装詳細から独立しています。
    """

    id: int
    worker_id: int
    organization_id: int  # マルチテナントキー（営業支援会社）
    client_organization_id: int | None
    title: str
    content: str
    status: str  # pending, in_review, answered, closed
    priority: str  # low, medium, high, urgent
    answer: str | None
    answered_by_user_id: int | None
    answered_at: datetime | None
    tags: str | None
    internal_notes: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_pending(self) -> bool:
        """未対応状態かを判定"""
        return self.status == "pending"

    def is_answered(self) -> bool:
        """回答済みかを判定"""
        return self.status == "answered"

    def can_be_answered(self) -> bool:
        """回答可能な状態かを判定"""
        return self.status in ["pending", "in_review"] and not self.is_deleted()

    def can_be_closed(self) -> bool:
        """クローズ可能な状態かを判定"""
        return self.status in ["pending", "in_review", "answered"] and not self.is_deleted()
