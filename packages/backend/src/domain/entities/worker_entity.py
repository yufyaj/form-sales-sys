"""
ワーカーエンティティ

ドメイン層のワーカーモデル。フォーム営業の実務作業者情報を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime

from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus


@dataclass
class WorkerEntity:
    """
    ワーカーエンティティ

    フォーム営業の実務作業者情報をビジネスロジックの観点から表現します。
    Userテーブルと1:1の関係を持ち、ワーカー固有の情報を管理します。
    """

    id: int
    user_id: int  # FK to users.id (1:1)
    organization_id: int  # FK to organizations.id (営業支援会社)
    status: WorkerStatus  # ワーカーステータス
    skill_level: SkillLevel | None = None  # スキルレベル
    experience_months: int | None = None  # 経験月数
    specialties: str | None = None  # 得意分野・専門領域
    max_tasks_per_day: int | None = None  # 1日の最大タスク数
    available_hours_per_week: int | None = None  # 週間稼働可能時間
    completed_tasks_count: int = 0  # 完了タスク数
    success_rate: float | None = None  # 成功率（%）
    average_task_time_minutes: int | None = None  # 平均タスク処理時間（分）
    rating: float | None = None  # 評価スコア（5段階）
    notes: str | None = None  # 管理者用メモ・備考
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """稼働中かを判定"""
        return self.status == WorkerStatus.ACTIVE and not self.is_deleted()

    def can_accept_tasks(self) -> bool:
        """タスクを受け入れ可能かを判定"""
        return self.status == WorkerStatus.ACTIVE and not self.is_deleted()

    def has_skill_info(self) -> bool:
        """スキル情報が設定されているかを判定"""
        return self.skill_level is not None or self.experience_months is not None
