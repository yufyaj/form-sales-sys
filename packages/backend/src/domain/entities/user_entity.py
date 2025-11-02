"""
ユーザーエンティティ

ドメイン層のユーザーモデル。ビジネスロジックの中核を担います。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    """
    ユーザーエンティティ

    ビジネスロジックの観点からのユーザーを表現します。
    データベースの実装詳細から独立しています。
    """

    id: int
    organization_id: int
    email: str
    hashed_password: str
    full_name: str
    phone: str | None
    avatar_url: str | None
    description: str | None
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def can_login(self) -> bool:
        """ログイン可能かを判定"""
        return self.is_active and not self.is_deleted()
