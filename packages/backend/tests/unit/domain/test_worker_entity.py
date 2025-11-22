"""
ワーカーエンティティのユニットテスト

ビジネスロジックとバリデーションをテストします。
"""
from datetime import datetime

import pytest

from src.domain.entities.worker_entity import WorkerEntity
from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus


class TestWorkerEntity:
    """WorkerEntityのテストクラス"""

    def test_create_worker_entity_with_minimal_fields(self) -> None:
        """最小限のフィールドでワーカーエンティティを作成"""
        # Arrange & Act
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.PENDING,
        )

        # Assert
        assert worker.id == 1
        assert worker.user_id == 10
        assert worker.organization_id == 20
        assert worker.status == WorkerStatus.PENDING
        assert worker.skill_level is None
        assert worker.experience_months is None
        assert worker.specialties is None
        assert worker.max_tasks_per_day is None
        assert worker.available_hours_per_week is None
        assert worker.completed_tasks_count == 0
        assert worker.success_rate is None
        assert worker.average_task_time_minutes is None
        assert worker.rating is None
        assert worker.notes is None

    def test_create_worker_entity_with_all_fields(self) -> None:
        """全フィールドを指定してワーカーエンティティを作成"""
        # Arrange
        created = datetime(2025, 1, 1, 10, 0, 0)
        updated = datetime(2025, 1, 10, 15, 30, 0)

        # Act
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            skill_level=SkillLevel.INTERMEDIATE,
            experience_months=12,
            specialties="BtoB営業、IT業界",
            max_tasks_per_day=10,
            available_hours_per_week=40,
            completed_tasks_count=50,
            success_rate=85.5,
            average_task_time_minutes=30,
            rating=4.5,
            notes="優秀なワーカー",
            created_at=created,
            updated_at=updated,
        )

        # Assert
        assert worker.id == 1
        assert worker.user_id == 10
        assert worker.organization_id == 20
        assert worker.status == WorkerStatus.ACTIVE
        assert worker.skill_level == SkillLevel.INTERMEDIATE
        assert worker.experience_months == 12
        assert worker.specialties == "BtoB営業、IT業界"
        assert worker.max_tasks_per_day == 10
        assert worker.available_hours_per_week == 40
        assert worker.completed_tasks_count == 50
        assert worker.success_rate == 85.5
        assert worker.average_task_time_minutes == 30
        assert worker.rating == 4.5
        assert worker.notes == "優秀なワーカー"
        assert worker.created_at == created
        assert worker.updated_at == updated
        assert worker.deleted_at is None

    def test_is_deleted_returns_false_when_not_deleted(self) -> None:
        """論理削除されていない場合、is_deleted()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            deleted_at=None,
        )

        # Act & Assert
        assert worker.is_deleted() is False

    def test_is_deleted_returns_true_when_deleted(self) -> None:
        """論理削除されている場合、is_deleted()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert worker.is_deleted() is True

    def test_is_active_returns_true_for_active_status(self) -> None:
        """ACTIVEステータスの場合、is_active()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
        )

        # Act & Assert
        assert worker.is_active() is True

    def test_is_active_returns_false_for_pending_status(self) -> None:
        """PENDINGステータスの場合、is_active()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.PENDING,
        )

        # Act & Assert
        assert worker.is_active() is False

    def test_is_active_returns_false_for_inactive_status(self) -> None:
        """INACTIVEステータスの場合、is_active()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.INACTIVE,
        )

        # Act & Assert
        assert worker.is_active() is False

    def test_is_active_returns_false_for_suspended_status(self) -> None:
        """SUSPENDEDステータスの場合、is_active()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.SUSPENDED,
        )

        # Act & Assert
        assert worker.is_active() is False

    def test_is_active_returns_false_when_deleted(self) -> None:
        """削除済みの場合、is_active()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert worker.is_active() is False

    def test_can_accept_tasks_returns_true_for_active_worker(self) -> None:
        """稼働中のワーカーの場合、can_accept_tasks()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
        )

        # Act & Assert
        assert worker.can_accept_tasks() is True

    def test_can_accept_tasks_returns_false_for_pending_worker(self) -> None:
        """承認待ちのワーカーの場合、can_accept_tasks()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.PENDING,
        )

        # Act & Assert
        assert worker.can_accept_tasks() is False

    def test_can_accept_tasks_returns_false_when_deleted(self) -> None:
        """削除済みの場合、can_accept_tasks()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert worker.can_accept_tasks() is False

    def test_has_skill_info_returns_true_when_skill_level_set(self) -> None:
        """スキルレベルが設定されている場合、has_skill_info()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            skill_level=SkillLevel.INTERMEDIATE,
        )

        # Act & Assert
        assert worker.has_skill_info() is True

    def test_has_skill_info_returns_true_when_experience_months_set(self) -> None:
        """経験月数が設定されている場合、has_skill_info()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            experience_months=12,
        )

        # Act & Assert
        assert worker.has_skill_info() is True

    def test_has_skill_info_returns_true_when_both_set(self) -> None:
        """スキルレベルと経験月数の両方が設定されている場合、has_skill_info()はTrueを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
            skill_level=SkillLevel.ADVANCED,
            experience_months=24,
        )

        # Act & Assert
        assert worker.has_skill_info() is True

    def test_has_skill_info_returns_false_when_no_skill_info(self) -> None:
        """スキル情報が設定されていない場合、has_skill_info()はFalseを返す"""
        # Arrange
        worker = WorkerEntity(
            id=1,
            user_id=10,
            organization_id=20,
            status=WorkerStatus.ACTIVE,
        )

        # Act & Assert
        assert worker.has_skill_info() is False

    def test_worker_with_all_skill_levels(self) -> None:
        """全てのスキルレベルでワーカーを作成できることを確認"""
        # Arrange & Act & Assert
        for skill_level in [
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
        ]:
            worker = WorkerEntity(
                id=1,
                user_id=10,
                organization_id=20,
                status=WorkerStatus.ACTIVE,
                skill_level=skill_level,
            )
            assert worker.skill_level == skill_level

    def test_worker_with_all_statuses(self) -> None:
        """全てのステータスでワーカーを作成できることを確認"""
        # Arrange & Act & Assert
        for status in [
            WorkerStatus.PENDING,
            WorkerStatus.ACTIVE,
            WorkerStatus.INACTIVE,
            WorkerStatus.SUSPENDED,
        ]:
            worker = WorkerEntity(
                id=1,
                user_id=10,
                organization_id=20,
                status=status,
            )
            assert worker.status == status
