"""
プロジェクトエンティティ

ドメイン層のプロジェクトモデル。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """プロジェクトステータス"""

    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    """プロジェクト優先度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProjectEntity:
    """
    プロジェクトエンティティ

    プロジェクト情報をビジネスロジックの観点から表現します。
    """

    id: int
    client_organization_id: int
    name: str
    status: ProjectStatus
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    estimated_budget: int | None = None
    actual_budget: int | None = None
    priority: ProjectPriority | None = None
    owner_user_id: int | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """アクティブなプロジェクトかを判定"""
        return self.status in [
            ProjectStatus.PLANNING,
            ProjectStatus.IN_PROGRESS,
        ]

    def is_overdue(self) -> bool:
        """期限超過かを判定"""
        if self.end_date is None:
            return False
        from datetime import date as date_type

        return self.status == ProjectStatus.IN_PROGRESS and self.end_date < date_type.today()

    def calculate_budget_variance(self) -> int | None:
        """予算差異を計算（実績 - 見積）"""
        if self.estimated_budget is None or self.actual_budget is None:
            return None
        return self.actual_budget - self.estimated_budget

    def validate_date_range(self) -> None:
        """
        日付範囲の妥当性を検証

        Raises:
            InvalidDateRangeError: 開始日が終了日より後の場合
        """
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                from src.domain.exceptions import InvalidDateRangeError

                raise InvalidDateRangeError(
                    str(self.start_date), str(self.end_date)
                )

    def validate_budgets(self) -> None:
        """
        予算値の妥当性を検証

        Raises:
            InvalidBudgetError: 予算値が負の場合
        """
        from src.domain.exceptions import InvalidBudgetError

        if self.estimated_budget is not None and self.estimated_budget < 0:
            raise InvalidBudgetError("見積予算", self.estimated_budget)

        if self.actual_budget is not None and self.actual_budget < 0:
            raise InvalidBudgetError("実績予算", self.actual_budget)

    def validate(self) -> None:
        """
        プロジェクトエンティティの全バリデーションを実行

        Raises:
            InvalidDateRangeError: 日付範囲が不正な場合
            InvalidBudgetError: 予算値が不正な場合
        """
        self.validate_date_range()
        self.validate_budgets()
