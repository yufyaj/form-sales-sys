"""
プロジェクトエンティティ

ドメイン層のプロジェクトモデル。プロジェクトのビジネスロジックを管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """プロジェクトステータス"""

    PLANNING = "planning"  # 計画中
    ACTIVE = "active"  # 進行中
    PAUSED = "paused"  # 一時停止
    COMPLETED = "completed"  # 完了
    ARCHIVED = "archived"  # アーカイブ


@dataclass
class ProjectEntity:
    """
    プロジェクトエンティティ

    顧客組織に紐づくプロジェクト情報をビジネスロジックの観点から表現します。
    """

    id: int
    organization_id: int  # FK to organizations.id（マルチテナント用）
    client_organization_id: int  # FK to client_organizations.id
    name: str
    status: ProjectStatus
    progress: int = 0  # 進捗率（0-100）
    total_lists: int = 0  # 総リスト数
    completed_lists: int = 0  # 完了リスト数
    total_submissions: int = 0  # 総送信数
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """アクティブなプロジェクトかを判定"""
        return self.status == ProjectStatus.ACTIVE and not self.is_deleted()

    def is_completed(self) -> bool:
        """完了したプロジェクトかを判定"""
        return self.status == ProjectStatus.COMPLETED

    def can_be_edited(self) -> bool:
        """編集可能かを判定（アーカイブ済みまたは削除済みは編集不可）"""
        return self.status != ProjectStatus.ARCHIVED and not self.is_deleted()

    def calculate_progress(self) -> int:
        """
        進捗率を計算

        総リスト数が0の場合は0を返す。
        それ以外は、完了リスト数 / 総リスト数 * 100 を返す。
        """
        if self.total_lists == 0:
            return 0
        return min(100, int((self.completed_lists / self.total_lists) * 100))

    def validate_progress_range(self) -> bool:
        """進捗率が0-100の範囲内かを検証"""
        return 0 <= self.progress <= 100

    def validate_lists_consistency(self) -> bool:
        """リスト数の整合性を検証（完了リスト数 <= 総リスト数）"""
        return (
            self.total_lists >= 0
            and self.completed_lists >= 0
            and self.completed_lists <= self.total_lists
        )

    def validate_submissions_non_negative(self) -> bool:
        """総送信数が0以上かを検証"""
        return self.total_submissions >= 0

    def is_valid(self) -> bool:
        """エンティティ全体の妥当性を検証"""
        return (
            self.validate_progress_range()
            and self.validate_lists_consistency()
            and self.validate_submissions_non_negative()
        )
