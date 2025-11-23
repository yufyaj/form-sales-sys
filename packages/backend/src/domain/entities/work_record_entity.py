"""
作業記録エンティティ

ドメイン層の作業記録モデル。ワーカーがリストアイテムに対して実施したフォーム送信作業の記録を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.infrastructure.persistence.models.work_record import WorkRecordStatus


@dataclass
class WorkRecordEntity:
    """
    作業記録エンティティ

    ワーカーがリストアイテムに対して実施したフォーム送信作業の記録をビジネスロジックの観点から表現します。
    送信済み/送信不可のステータス、作業日時、送信結果の詳細を管理します。
    """

    id: int
    assignment_id: int  # FK to list_item_assignments.id
    worker_id: int  # FK to workers.id
    status: WorkRecordStatus  # 送信済み or 送信不可
    started_at: datetime  # 作業開始日時
    completed_at: datetime  # 作業完了日時
    form_submission_result: dict[str, Any] | None = None  # 送信結果の詳細（JSON）
    cannot_send_reason_id: int | None = None  # FK to cannot_send_reasons.id
    notes: str | None = None  # メモ・備考
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_sent(self) -> bool:
        """送信済みかを判定"""
        return self.status == WorkRecordStatus.SENT

    def is_cannot_send(self) -> bool:
        """送信不可かを判定"""
        return self.status == WorkRecordStatus.CANNOT_SEND

    def get_duration_minutes(self) -> int:
        """作業時間を分単位で取得"""
        duration = self.completed_at - self.started_at
        return int(duration.total_seconds() / 60)

    def has_submission_result(self) -> bool:
        """送信結果の詳細があるかを判定"""
        return self.form_submission_result is not None and len(self.form_submission_result) > 0
