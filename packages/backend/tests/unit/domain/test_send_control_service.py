"""
送信制御ドメインサービスのユニットテスト

送信可能かどうかを判定するビジネスロジックをテストします。
TDDサイクル: Red -> Green -> Refactor
"""
from datetime import datetime, time, date, timezone

import pytest

from src.domain.entities.no_send_setting_entity import (
    NoSendSettingEntity,
    NoSendSettingType,
)
from src.domain.services.send_control_service import SendControlService


class TestSendControlService:
    """SendControlServiceのテストクラス"""

    def test_can_send_when_no_restrictions(self) -> None:
        """送信禁止設定がない場合、送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 20, 14, 30, 0, tzinfo=timezone.utc)  # 月曜 14:30
        settings: list[NoSendSettingEntity] = []

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_cannot_send_on_prohibited_day_of_week(self) -> None:
        """禁止曜日（土曜）に送信不可と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 25, 14, 30, 0, tzinfo=timezone.utc)  # 土曜 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.DAY_OF_WEEK,
                name="週末の送信禁止",
                is_enabled=True,
                day_of_week_list=[6, 7],  # 土日
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止曜日: 週末の送信禁止"

    def test_can_send_on_non_prohibited_day_of_week(self) -> None:
        """禁止曜日（土日）以外は送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 20, 14, 30, 0, tzinfo=timezone.utc)  # 月曜 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.DAY_OF_WEEK,
                name="週末の送信禁止",
                is_enabled=True,
                day_of_week_list=[6, 7],  # 土日
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_cannot_send_during_prohibited_time_range(self) -> None:
        """禁止時間帯（深夜）に送信不可と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 20, 23, 30, 0, tzinfo=timezone.utc)  # 23:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.TIME_RANGE,
                name="深夜の送信禁止",
                is_enabled=True,
                time_start=time(22, 0, 0),  # 22:00
                time_end=time(6, 0, 0),  # 6:00 (翌日)
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止時間帯: 深夜の送信禁止"

    def test_can_send_outside_prohibited_time_range(self) -> None:
        """禁止時間帯外は送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 20, 14, 30, 0, tzinfo=timezone.utc)  # 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.TIME_RANGE,
                name="深夜の送信禁止",
                is_enabled=True,
                time_start=time(22, 0, 0),  # 22:00
                time_end=time(6, 0, 0),  # 6:00 (翌日)
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_cannot_send_during_midnight_crossing_time_range(self) -> None:
        """日を跨ぐ禁止時間帯（22:00-6:00）で深夜1:00は送信不可と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 20, 1, 0, 0, tzinfo=timezone.utc)  # 1:00 (深夜)
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.TIME_RANGE,
                name="深夜の送信禁止",
                is_enabled=True,
                time_start=time(22, 0, 0),  # 22:00
                time_end=time(6, 0, 0),  # 6:00 (翌日)
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止時間帯: 深夜の送信禁止"

    def test_cannot_send_on_specific_prohibited_date(self) -> None:
        """特定の禁止日（2025-01-01）に送信不可と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 1, 14, 30, 0, tzinfo=timezone.utc)  # 2025-01-01 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.SPECIFIC_DATE,
                name="元日の送信禁止",
                is_enabled=True,
                specific_date=date(2025, 1, 1),
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止日: 元日の送信禁止"

    def test_can_send_on_non_specific_prohibited_date(self) -> None:
        """特定の禁止日以外は送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 2, 14, 30, 0, tzinfo=timezone.utc)  # 2025-01-02 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.SPECIFIC_DATE,
                name="元日の送信禁止",
                is_enabled=True,
                specific_date=date(2025, 1, 1),
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_cannot_send_during_prohibited_date_range(self) -> None:
        """禁止日付範囲（年末年始）に送信不可と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 2, 14, 30, 0, tzinfo=timezone.utc)  # 2025-01-02 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.SPECIFIC_DATE,
                name="年末年始の送信禁止",
                is_enabled=True,
                date_range_start=date(2024, 12, 29),
                date_range_end=date(2025, 1, 3),
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止期間: 年末年始の送信禁止"

    def test_can_send_outside_prohibited_date_range(self) -> None:
        """禁止日付範囲外は送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 4, 14, 30, 0, tzinfo=timezone.utc)  # 2025-01-04 14:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.SPECIFIC_DATE,
                name="年末年始の送信禁止",
                is_enabled=True,
                date_range_start=date(2024, 12, 29),
                date_range_end=date(2025, 1, 3),
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_cannot_send_when_multiple_restrictions_apply(self) -> None:
        """複数の禁止設定が適用される場合、最初の禁止理由を返す"""
        # Arrange
        check_datetime = datetime(2025, 1, 25, 23, 30, 0, tzinfo=timezone.utc)  # 土曜 23:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.DAY_OF_WEEK,
                name="週末の送信禁止",
                is_enabled=True,
                day_of_week_list=[6, 7],
            ),
            NoSendSettingEntity(
                id=2,
                list_id=1,
                setting_type=NoSendSettingType.TIME_RANGE,
                name="深夜の送信禁止",
                is_enabled=True,
                time_start=time(22, 0, 0),
                time_end=time(6, 0, 0),
            ),
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is False
        assert reason == "禁止曜日: 週末の送信禁止"  # 最初の設定が優先される

    def test_can_send_when_all_settings_are_disabled(self) -> None:
        """すべての禁止設定が無効の場合、送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 25, 23, 30, 0, tzinfo=timezone.utc)  # 土曜 23:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.DAY_OF_WEEK,
                name="週末の送信禁止",
                is_enabled=False,  # 無効
                day_of_week_list=[6, 7],
            ),
            NoSendSettingEntity(
                id=2,
                list_id=1,
                setting_type=NoSendSettingType.TIME_RANGE,
                name="深夜の送信禁止",
                is_enabled=False,  # 無効
                time_start=time(22, 0, 0),
                time_end=time(6, 0, 0),
            ),
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None

    def test_can_send_when_all_settings_are_deleted(self) -> None:
        """すべての禁止設定が論理削除済みの場合、送信可能と判定する"""
        # Arrange
        check_datetime = datetime(2025, 1, 25, 23, 30, 0, tzinfo=timezone.utc)  # 土曜 23:30
        settings = [
            NoSendSettingEntity(
                id=1,
                list_id=1,
                setting_type=NoSendSettingType.DAY_OF_WEEK,
                name="週末の送信禁止",
                is_enabled=True,
                day_of_week_list=[6, 7],
                deleted_at=datetime.now(timezone.utc),  # 論理削除済み
            )
        ]

        # Act
        can_send, reason = SendControlService.can_send_at(settings, check_datetime)

        # Assert
        assert can_send is True
        assert reason is None
