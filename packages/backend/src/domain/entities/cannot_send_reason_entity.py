"""
送信不可理由エンティティ

ドメイン層の送信不可理由モデル。フォーム送信が不可能な理由のマスターデータを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CannotSendReasonEntity:
    """
    送信不可理由エンティティ

    フォーム送信が不可能な理由のマスターデータをビジネスロジックの観点から表現します。
    work_recordsから参照されます。
    """

    id: int
    reason_code: str  # 理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）
    reason_name: str  # 理由名
    description: str | None = None  # 詳細説明
    is_active: bool = True  # 有効/無効フラグ
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_usable(self) -> bool:
        """使用可能かを判定（有効かつ削除されていない）"""
        return self.is_active and not self.is_deleted()
