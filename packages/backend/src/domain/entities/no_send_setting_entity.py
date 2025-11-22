"""
送信禁止設定エンティティ

ドメイン層の送信禁止設定モデル。
営業メール等の自動送信を禁止する時間帯・曜日・日付を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime, date, time
from enum import Enum


class NoSendSettingType(str, Enum):
    """送信禁止設定の種類"""
    DAY_OF_WEEK = "day_of_week"      # 曜日指定
    TIME_RANGE = "time_range"         # 時間帯指定
    SPECIFIC_DATE = "specific_date"   # 特定日付指定


class DayOfWeek(int, Enum):
    """曜日の列挙型 (ISO 8601準拠: 月曜=1, 日曜=7)"""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


@dataclass
class NoSendSettingEntity:
    """
    送信禁止設定エンティティ

    営業メール等の自動送信を禁止する時間帯・曜日・日付をビジネスロジックの観点から表現します。
    各設定はリストに紐付きます。
    """

    id: int
    list_id: int  # FK to lists.id
    setting_type: NoSendSettingType  # 設定種別
    name: str  # 設定名
    description: str | None = None  # 設定の説明
    is_enabled: bool = True  # 有効/無効フラグ

    # 曜日設定（setting_type=day_of_weekの場合に使用）
    day_of_week_list: list[int] | None = None

    # 時間帯設定（setting_type=time_rangeの場合に使用）
    time_start: time | None = None
    time_end: time | None = None

    # 日付設定（setting_type=specific_dateの場合に使用）
    specific_date: date | None = None
    date_range_start: date | None = None
    date_range_end: date | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_name(self) -> bool:
        """設定名が設定されているかを判定"""
        return bool(self.name and self.name.strip())

    def is_day_of_week_setting(self) -> bool:
        """曜日ベースの設定かどうかを判定"""
        return self.setting_type == NoSendSettingType.DAY_OF_WEEK

    def is_time_range_setting(self) -> bool:
        """時間帯ベースの設定かどうかを判定"""
        return self.setting_type == NoSendSettingType.TIME_RANGE

    def is_specific_date_setting(self) -> bool:
        """特定日付の設定かどうかを判定"""
        return self.setting_type == NoSendSettingType.SPECIFIC_DATE

    def is_active(self) -> bool:
        """設定が有効で削除されていないかを判定"""
        return self.is_enabled and not self.is_deleted()
