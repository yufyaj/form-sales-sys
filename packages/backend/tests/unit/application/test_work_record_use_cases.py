"""
作業記録ユースケースのユニットテスト

TDDサイクル: Red -> Green -> Refactor
リポジトリはモックで代替し、ビジネスロジックのみをテストします。
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.schemas.work_record import (
    WorkRecordCreateRequest,
    FormSubmissionResult,
)
from src.application.use_cases.work_record_use_cases import WorkRecordUseCases
from src.domain.entities.work_record_entity import WorkRecordEntity
from src.domain.entities.no_send_setting_entity import NoSendSettingEntity, NoSendSettingType
from src.domain.exceptions import WorkRecordNotFoundError
from src.infrastructure.persistence.models.work_record import WorkRecordStatus


@pytest.fixture
def mock_work_record_repo():
    """作業記録リポジトリのモック"""
    return AsyncMock()


@pytest.fixture
def mock_no_send_setting_repo():
    """送信禁止設定リポジトリのモック"""
    return AsyncMock()


@pytest.fixture
def work_record_use_cases(mock_work_record_repo, mock_no_send_setting_repo):
    """作業記録ユースケースのインスタンス"""
    return WorkRecordUseCases(
        work_record_repository=mock_work_record_repo,
        no_send_setting_repository=mock_no_send_setting_repo,
    )


class TestWorkRecordUseCases:
    """WorkRecordUseCasesのテストクラス"""

    async def test_create_work_record_with_sent_status(
        self,
        work_record_use_cases: WorkRecordUseCases,
        mock_work_record_repo: AsyncMock,
        mock_no_send_setting_repo: AsyncMock,
    ) -> None:
        """送信済みステータスで作業記録を作成できる"""
        # Arrange
        request = WorkRecordCreateRequest(
            assignment_id=1,
            worker_id=1,
            status=WorkRecordStatus.SENT,
            started_at=datetime(2025, 1, 20, 10, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2025, 1, 20, 10, 30, 0, tzinfo=timezone.utc),
            form_submission_result=FormSubmissionResult(status_code=200, message="送信成功"),
            notes="問題なく送信完了",
        )

        expected_entity = WorkRecordEntity(
            id=1,
            assignment_id=1,
            worker_id=1,
            status=WorkRecordStatus.SENT,
            started_at=request.started_at,
            completed_at=request.completed_at,
            form_submission_result=request.form_submission_result.model_dump() if request.form_submission_result else None,
            notes="問題なく送信完了",
        )

        mock_work_record_repo.create.return_value = expected_entity

        # Act
        result = await work_record_use_cases.create_work_record(request, list_id=1)

        # Assert
        assert result.id == 1
        assert result.status == WorkRecordStatus.SENT
        mock_work_record_repo.create.assert_called_once()

    async def test_create_work_record_with_cannot_send_status(
        self,
        work_record_use_cases: WorkRecordUseCases,
        mock_work_record_repo: AsyncMock,
    ) -> None:
        """送信不可ステータスで作業記録を作成できる"""
        # Arrange
        request = WorkRecordCreateRequest(
            assignment_id=1,
            worker_id=1,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=datetime(2025, 1, 20, 10, 0, 0, tzinfo=timezone.utc),
            completed_at=datetime(2025, 1, 20, 10, 15, 0, tzinfo=timezone.utc),
            cannot_send_reason_id=1,
            notes="フォームが見つからず",
        )

        expected_entity = WorkRecordEntity(
            id=2,
            assignment_id=1,
            worker_id=1,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=request.started_at,
            completed_at=request.completed_at,
            cannot_send_reason_id=1,
            notes="フォームが見つからず",
        )

        mock_work_record_repo.create.return_value = expected_entity

        # Act
        result = await work_record_use_cases.create_work_record(request, list_id=1)

        # Assert
        assert result.id == 2
        assert result.status == WorkRecordStatus.CANNOT_SEND
        assert result.cannot_send_reason_id == 1
        mock_work_record_repo.create.assert_called_once()
