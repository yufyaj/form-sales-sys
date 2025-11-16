"""
プロジェクトエンティティのユニットテスト

ビジネスロジックとバリデーションをテストします。
"""
from datetime import date, datetime, timedelta

import pytest

from src.domain.entities.project_entity import (
    ProjectEntity,
    ProjectPriority,
    ProjectStatus,
)
from src.domain.exceptions import InvalidBudgetError, InvalidDateRangeError


class TestProjectEntity:
    """ProjectEntityのテストクラス"""

    def test_create_project_entity_with_minimal_fields(self) -> None:
        """最小限のフィールドでプロジェクトエンティティを作成"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Assert
        assert project.id == 1
        assert project.client_organization_id == 10
        assert project.name == "テストプロジェクト"
        assert project.status == ProjectStatus.PLANNING
        assert project.description is None
        assert project.start_date is None
        assert project.end_date is None
        assert project.estimated_budget is None
        assert project.actual_budget is None
        assert project.priority is None
        assert project.owner_user_id is None
        assert project.notes is None

    def test_create_project_entity_with_all_fields(self) -> None:
        """全フィールドを指定してプロジェクトエンティティを作成"""
        # Arrange
        start = date(2025, 1, 1)
        end = date(2025, 3, 31)
        created = datetime(2025, 1, 1, 10, 0, 0)
        updated = datetime(2025, 1, 10, 15, 30, 0)

        # Act
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="新規Webサイト構築",
            status=ProjectStatus.IN_PROGRESS,
            description="コーポレートサイトのリニューアル",
            start_date=start,
            end_date=end,
            estimated_budget=5000000,
            actual_budget=4800000,
            priority=ProjectPriority.HIGH,
            owner_user_id=5,
            notes="Q1完了目標",
            created_at=created,
            updated_at=updated,
        )

        # Assert
        assert project.id == 1
        assert project.client_organization_id == 10
        assert project.name == "新規Webサイト構築"
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.description == "コーポレートサイトのリニューアル"
        assert project.start_date == start
        assert project.end_date == end
        assert project.estimated_budget == 5000000
        assert project.actual_budget == 4800000
        assert project.priority == ProjectPriority.HIGH
        assert project.owner_user_id == 5
        assert project.notes == "Q1完了目標"
        assert project.created_at == created
        assert project.updated_at == updated
        assert project.deleted_at is None

    def test_is_deleted_returns_false_when_not_deleted(self) -> None:
        """論理削除されていない場合、is_deleted()はFalseを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            deleted_at=None,
        )

        # Act & Assert
        assert project.is_deleted() is False

    def test_is_deleted_returns_true_when_deleted(self) -> None:
        """論理削除されている場合、is_deleted()はTrueを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert project.is_deleted() is True

    def test_is_active_returns_true_for_planning_status(self) -> None:
        """PLANNINGステータスの場合、is_active()はTrueを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act & Assert
        assert project.is_active() is True

    def test_is_active_returns_true_for_in_progress_status(self) -> None:
        """IN_PROGRESSステータスの場合、is_active()はTrueを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
        )

        # Act & Assert
        assert project.is_active() is True

    def test_is_active_returns_false_for_on_hold_status(self) -> None:
        """ON_HOLDステータスの場合、is_active()はFalseを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ON_HOLD,
        )

        # Act & Assert
        assert project.is_active() is False

    def test_is_active_returns_false_for_completed_status(self) -> None:
        """COMPLETEDステータスの場合、is_active()はFalseを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.COMPLETED,
        )

        # Act & Assert
        assert project.is_active() is False

    def test_is_active_returns_false_for_cancelled_status(self) -> None:
        """CANCELLEDステータスの場合、is_active()はFalseを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.CANCELLED,
        )

        # Act & Assert
        assert project.is_active() is False

    def test_is_overdue_returns_false_when_no_end_date(self) -> None:
        """終了日が設定されていない場合、is_overdue()はFalseを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            end_date=None,
        )

        # Act & Assert
        assert project.is_overdue() is False

    def test_is_overdue_returns_false_when_end_date_is_future(self) -> None:
        """終了日が未来の場合、is_overdue()はFalseを返す"""
        # Arrange
        future_date = date.today() + timedelta(days=30)
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            end_date=future_date,
        )

        # Act & Assert
        assert project.is_overdue() is False

    def test_is_overdue_returns_true_when_end_date_is_past_and_in_progress(self) -> None:
        """終了日が過去でIN_PROGRESSの場合、is_overdue()はTrueを返す"""
        # Arrange
        past_date = date.today() - timedelta(days=1)
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            end_date=past_date,
        )

        # Act & Assert
        assert project.is_overdue() is True

    def test_is_overdue_returns_false_when_end_date_is_past_but_completed(self) -> None:
        """終了日が過去でもCOMPLETEDの場合、is_overdue()はFalseを返す"""
        # Arrange
        past_date = date.today() - timedelta(days=1)
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.COMPLETED,
            end_date=past_date,
        )

        # Act & Assert
        assert project.is_overdue() is False

    def test_calculate_budget_variance_returns_none_when_no_budgets(self) -> None:
        """予算が設定されていない場合、calculate_budget_variance()はNoneを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
        )

        # Act & Assert
        assert project.calculate_budget_variance() is None

    def test_calculate_budget_variance_returns_none_when_only_estimated_budget(
        self,
    ) -> None:
        """見積予算のみ設定されている場合、calculate_budget_variance()はNoneを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            estimated_budget=5000000,
        )

        # Act & Assert
        assert project.calculate_budget_variance() is None

    def test_calculate_budget_variance_returns_none_when_only_actual_budget(
        self,
    ) -> None:
        """実績予算のみ設定されている場合、calculate_budget_variance()はNoneを返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            actual_budget=4800000,
        )

        # Act & Assert
        assert project.calculate_budget_variance() is None

    def test_calculate_budget_variance_returns_positive_when_over_budget(self) -> None:
        """予算超過の場合、calculate_budget_variance()は正の値を返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            estimated_budget=5000000,
            actual_budget=5500000,
        )

        # Act
        variance = project.calculate_budget_variance()

        # Assert
        assert variance == 500000

    def test_calculate_budget_variance_returns_negative_when_under_budget(self) -> None:
        """予算内の場合、calculate_budget_variance()は負の値を返す"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            estimated_budget=5000000,
            actual_budget=4800000,
        )

        # Act
        variance = project.calculate_budget_variance()

        # Assert
        assert variance == -200000

    def test_validate_date_range_succeeds_when_dates_are_valid(self) -> None:
        """開始日が終了日より前の場合、validate_date_range()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
        )

        # Act & Assert
        project.validate_date_range()  # 例外が発生しないことを確認

    def test_validate_date_range_succeeds_when_no_dates(self) -> None:
        """日付が設定されていない場合、validate_date_range()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act & Assert
        project.validate_date_range()  # 例外が発生しないことを確認

    def test_validate_date_range_succeeds_when_only_start_date(self) -> None:
        """開始日のみ設定されている場合、validate_date_range()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 1, 1),
        )

        # Act & Assert
        project.validate_date_range()  # 例外が発生しないことを確認

    def test_validate_date_range_raises_error_when_start_after_end(self) -> None:
        """開始日が終了日より後の場合、validate_date_range()は例外を発生させる"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 3, 31),
            end_date=date(2025, 1, 1),
        )

        # Act & Assert
        with pytest.raises(InvalidDateRangeError) as exc_info:
            project.validate_date_range()

        assert "2025-03-31" in str(exc_info.value)
        assert "2025-01-01" in str(exc_info.value)

    def test_validate_budgets_succeeds_when_budgets_are_positive(self) -> None:
        """予算が正の値の場合、validate_budgets()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            estimated_budget=5000000,
            actual_budget=4800000,
        )

        # Act & Assert
        project.validate_budgets()  # 例外が発生しないことを確認

    def test_validate_budgets_succeeds_when_budgets_are_zero(self) -> None:
        """予算が0の場合、validate_budgets()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            estimated_budget=0,
            actual_budget=0,
        )

        # Act & Assert
        project.validate_budgets()  # 例外が発生しないことを確認

    def test_validate_budgets_succeeds_when_no_budgets(self) -> None:
        """予算が設定されていない場合、validate_budgets()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act & Assert
        project.validate_budgets()  # 例外が発生しないことを確認

    def test_validate_budgets_raises_error_when_estimated_budget_is_negative(
        self,
    ) -> None:
        """見積予算が負の値の場合、validate_budgets()は例外を発生させる"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            estimated_budget=-1000,
        )

        # Act & Assert
        with pytest.raises(InvalidBudgetError) as exc_info:
            project.validate_budgets()

        assert "見積予算" in str(exc_info.value)
        assert "-1000" in str(exc_info.value)

    def test_validate_budgets_raises_error_when_actual_budget_is_negative(
        self,
    ) -> None:
        """実績予算が負の値の場合、validate_budgets()は例外を発生させる"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            actual_budget=-1000,
        )

        # Act & Assert
        with pytest.raises(InvalidBudgetError) as exc_info:
            project.validate_budgets()

        assert "実績予算" in str(exc_info.value)
        assert "-1000" in str(exc_info.value)

    def test_validate_succeeds_when_all_validations_pass(self) -> None:
        """全バリデーションが成功する場合、validate()は成功する"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            estimated_budget=5000000,
            actual_budget=4800000,
        )

        # Act & Assert
        project.validate()  # 例外が発生しないことを確認

    def test_validate_raises_error_when_date_range_is_invalid(self) -> None:
        """日付範囲が不正な場合、validate()は例外を発生させる"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 3, 31),
            end_date=date(2025, 1, 1),
        )

        # Act & Assert
        with pytest.raises(InvalidDateRangeError):
            project.validate()

    def test_validate_raises_error_when_budget_is_invalid(self) -> None:
        """予算が不正な場合、validate()は例外を発生させる"""
        # Arrange
        project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            estimated_budget=-1000,
        )

        # Act & Assert
        with pytest.raises(InvalidBudgetError):
            project.validate()
