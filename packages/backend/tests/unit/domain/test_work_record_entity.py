"""
作業記録エンティティのユニットテスト

ビジネスロジックとバリデーションをテストします。
"""
from datetime import datetime, timedelta

import pytest

from src.domain.entities.work_record_entity import WorkRecordEntity
from src.infrastructure.persistence.models.work_record import WorkRecordStatus


class TestWorkRecordEntity:
    """WorkRecordEntityのテストクラス"""

    def test_create_work_record_entity_with_sent_status(self) -> None:
        """送信済みステータスで作業記録エンティティを作成"""
        # Arrange
        started = datetime(2025, 11, 22, 10, 0, 0)
        completed = datetime(2025, 11, 22, 10, 30, 0)

        # Act
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=started,
            completed_at=completed,
            form_submission_result={"status_code": 200, "message": "送信成功"},
            notes="問題なく送信完了",
        )

        # Assert
        assert record.id == 1
        assert record.assignment_id == 100
        assert record.worker_id == 200
        assert record.status == WorkRecordStatus.SENT
        assert record.started_at == started
        assert record.completed_at == completed
        assert record.form_submission_result == {"status_code": 200, "message": "送信成功"}
        assert record.cannot_send_reason_id is None
        assert record.notes == "問題なく送信完了"

    def test_create_work_record_entity_with_cannot_send_status(self) -> None:
        """送信不可ステータスで作業記録エンティティを作成"""
        # Arrange
        started = datetime(2025, 11, 22, 11, 0, 0)
        completed = datetime(2025, 11, 22, 11, 15, 0)

        # Act
        record = WorkRecordEntity(
            id=2,
            assignment_id=101,
            worker_id=200,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=started,
            completed_at=completed,
            cannot_send_reason_id=5,
            notes="フォームが見つからず",
        )

        # Assert
        assert record.id == 2
        assert record.assignment_id == 101
        assert record.worker_id == 200
        assert record.status == WorkRecordStatus.CANNOT_SEND
        assert record.started_at == started
        assert record.completed_at == completed
        assert record.form_submission_result is None
        assert record.cannot_send_reason_id == 5
        assert record.notes == "フォームが見つからず"

    def test_is_deleted_returns_false_when_not_deleted(self) -> None:
        """論理削除されていない場合、is_deleted()はFalseを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            deleted_at=None,
        )

        # Act & Assert
        assert record.is_deleted() is False

    def test_is_deleted_returns_true_when_deleted(self) -> None:
        """論理削除されている場合、is_deleted()はTrueを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert record.is_deleted() is True

    def test_is_sent_returns_true_for_sent_status(self) -> None:
        """送信済みステータスの場合、is_sent()はTrueを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        # Act & Assert
        assert record.is_sent() is True

    def test_is_sent_returns_false_for_cannot_send_status(self) -> None:
        """送信不可ステータスの場合、is_sent()はFalseを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        # Act & Assert
        assert record.is_sent() is False

    def test_is_cannot_send_returns_true_for_cannot_send_status(self) -> None:
        """送信不可ステータスの場合、is_cannot_send()はTrueを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        # Act & Assert
        assert record.is_cannot_send() is True

    def test_is_cannot_send_returns_false_for_sent_status(self) -> None:
        """送信済みステータスの場合、is_cannot_send()はFalseを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        # Act & Assert
        assert record.is_cannot_send() is False

    def test_get_duration_minutes_calculates_correctly(self) -> None:
        """作業時間（分）を正しく計算する"""
        # Arrange
        started = datetime(2025, 11, 22, 10, 0, 0)
        completed = datetime(2025, 11, 22, 10, 30, 0)

        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=started,
            completed_at=completed,
        )

        # Act
        duration = record.get_duration_minutes()

        # Assert
        assert duration == 30

    def test_get_duration_minutes_with_various_durations(self) -> None:
        """様々な作業時間で正しく計算できることを確認"""
        # Arrange & Act & Assert
        test_cases = [
            (5, 5),      # 5分
            (15, 15),    # 15分
            (60, 60),    # 1時間
            (90, 90),    # 1時間30分
            (120, 120),  # 2時間
        ]

        for minutes, expected in test_cases:
            started = datetime(2025, 11, 22, 10, 0, 0)
            completed = started + timedelta(minutes=minutes)

            record = WorkRecordEntity(
                id=1,
                assignment_id=100,
                worker_id=200,
                status=WorkRecordStatus.SENT,
                started_at=started,
                completed_at=completed,
            )

            assert record.get_duration_minutes() == expected

    def test_has_submission_result_returns_true_when_result_exists(self) -> None:
        """送信結果がある場合、has_submission_result()はTrueを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            form_submission_result={"status_code": 200, "message": "成功"},
        )

        # Act & Assert
        assert record.has_submission_result() is True

    def test_has_submission_result_returns_false_when_result_is_none(self) -> None:
        """送信結果がNoneの場合、has_submission_result()はFalseを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            form_submission_result=None,
        )

        # Act & Assert
        assert record.has_submission_result() is False

    def test_has_submission_result_returns_false_when_result_is_empty(self) -> None:
        """送信結果が空の場合、has_submission_result()はFalseを返す"""
        # Arrange
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            form_submission_result={},
        )

        # Act & Assert
        assert record.has_submission_result() is False

    def test_work_record_with_complex_submission_result(self) -> None:
        """複雑な送信結果を持つ作業記録を作成できることを確認"""
        # Arrange
        complex_result = {
            "status_code": 200,
            "message": "送信成功",
            "response_time_ms": 250,
            "headers": {
                "Content-Type": "application/json",
                "X-Request-ID": "abc123",
            },
            "retry_count": 1,
            "screenshot_url": "https://example.com/screenshot.png",
        }

        # Act
        record = WorkRecordEntity(
            id=1,
            assignment_id=100,
            worker_id=200,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            form_submission_result=complex_result,
        )

        # Assert
        assert record.form_submission_result == complex_result
        assert record.form_submission_result["status_code"] == 200
        assert record.form_submission_result["headers"]["X-Request-ID"] == "abc123"
        assert record.has_submission_result() is True
