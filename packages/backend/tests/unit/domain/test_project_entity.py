"""
プロジェクトエンティティの単体テスト

エンティティのビジネスロジックとバリデーションを検証します。
"""
from datetime import datetime, timezone

import pytest

from src.domain.entities.project_entity import ProjectEntity, ProjectStatus


class TestProjectEntity:
    """プロジェクトエンティティのテスト"""

    def test_is_deleted_when_deleted_at_is_none(self) -> None:
        """正常系：deleted_atがNoneの場合、削除されていない"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=None,
        )

        # Assert
        assert not project.is_deleted()

    def test_is_deleted_when_deleted_at_is_set(self) -> None:
        """正常系：deleted_atが設定されている場合、削除されている"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=datetime.now(timezone.utc),
        )

        # Assert
        assert project.is_deleted()

    def test_is_active_when_status_is_active_and_not_deleted(self) -> None:
        """正常系：ステータスがACTIVEで削除されていない場合、アクティブ"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=None,
        )

        # Assert
        assert project.is_active()

    def test_is_not_active_when_status_is_not_active(self) -> None:
        """正常系：ステータスがACTIVE以外の場合、アクティブではない"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
            deleted_at=None,
        )

        # Assert
        assert not project.is_active()

    def test_is_not_active_when_deleted(self) -> None:
        """正常系：削除されている場合、アクティブではない"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=datetime.now(timezone.utc),
        )

        # Assert
        assert not project.is_active()

    def test_is_completed_when_status_is_completed(self) -> None:
        """正常系：ステータスがCOMPLETEDの場合、完了している"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.COMPLETED,
        )

        # Assert
        assert project.is_completed()

    def test_can_be_edited_when_not_archived_and_not_deleted(self) -> None:
        """正常系：アーカイブ済みでも削除済みでもない場合、編集可能"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=None,
        )

        # Assert
        assert project.can_be_edited()

    def test_cannot_be_edited_when_archived(self) -> None:
        """正常系：アーカイブ済みの場合、編集不可"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ARCHIVED,
            deleted_at=None,
        )

        # Assert
        assert not project.can_be_edited()

    def test_cannot_be_edited_when_deleted(self) -> None:
        """正常系：削除済みの場合、編集不可"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            deleted_at=datetime.now(timezone.utc),
        )

        # Assert
        assert not project.can_be_edited()

    def test_calculate_progress_when_total_lists_is_zero(self) -> None:
        """正常系：総リスト数が0の場合、進捗率は0"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=0,
            completed_lists=0,
        )

        # Assert
        assert project.calculate_progress() == 0

    def test_calculate_progress_normal_case(self) -> None:
        """正常系：通常の進捗率計算"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=100,
            completed_lists=45,
        )

        # Assert
        assert project.calculate_progress() == 45

    def test_calculate_progress_rounds_down(self) -> None:
        """正常系：進捗率は切り捨て"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=3,
            completed_lists=1,
        )

        # Assert
        assert project.calculate_progress() == 33  # 33.33... -> 33

    def test_calculate_progress_capped_at_100(self) -> None:
        """正常系：進捗率は100を超えない"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=100,
            completed_lists=150,  # データ不整合の場合
        )

        # Assert
        assert project.calculate_progress() == 100

    def test_validate_progress_range_valid(self) -> None:
        """正常系：進捗率が0-100の範囲内の場合、バリデーション成功"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=50,
        )

        # Assert
        assert project.validate_progress_range()

    def test_validate_progress_range_invalid_negative(self) -> None:
        """異常系：進捗率が負の場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=-1,
        )

        # Assert
        assert not project.validate_progress_range()

    def test_validate_progress_range_invalid_over_100(self) -> None:
        """異常系：進捗率が100を超える場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=101,
        )

        # Assert
        assert not project.validate_progress_range()

    def test_validate_lists_consistency_valid(self) -> None:
        """正常系：リスト数の整合性が取れている場合、バリデーション成功"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=100,
            completed_lists=45,
        )

        # Assert
        assert project.validate_lists_consistency()

    def test_validate_lists_consistency_invalid_negative_total(self) -> None:
        """異常系：総リスト数が負の場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=-1,
            completed_lists=0,
        )

        # Assert
        assert not project.validate_lists_consistency()

    def test_validate_lists_consistency_invalid_negative_completed(self) -> None:
        """異常系：完了リスト数が負の場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=100,
            completed_lists=-1,
        )

        # Assert
        assert not project.validate_lists_consistency()

    def test_validate_lists_consistency_invalid_completed_exceeds_total(self) -> None:
        """異常系：完了リスト数が総リスト数を超える場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_lists=100,
            completed_lists=101,
        )

        # Assert
        assert not project.validate_lists_consistency()

    def test_validate_submissions_non_negative_valid(self) -> None:
        """正常系：総送信数が0以上の場合、バリデーション成功"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_submissions=1000,
        )

        # Assert
        assert project.validate_submissions_non_negative()

    def test_validate_submissions_non_negative_invalid(self) -> None:
        """異常系：総送信数が負の場合、バリデーション失敗"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            total_submissions=-1,
        )

        # Assert
        assert not project.validate_submissions_non_negative()

    def test_is_valid_all_validations_pass(self) -> None:
        """正常系：すべてのバリデーションが成功する場合、エンティティは有効"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=45,
            total_lists=100,
            completed_lists=45,
            total_submissions=1000,
        )

        # Assert
        assert project.is_valid()

    def test_is_valid_fails_when_any_validation_fails(self) -> None:
        """異常系：いずれかのバリデーションが失敗する場合、エンティティは無効"""
        # Arrange & Act
        project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=101,  # 無効な進捗率
            total_lists=100,
            completed_lists=45,
            total_submissions=1000,
        )

        # Assert
        assert not project.is_valid()
