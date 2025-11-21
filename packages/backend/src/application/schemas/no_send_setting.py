"""
NoSendSetting schema definitions using Pydantic

DTO schemas for API request/response validation and data transformation
FastAPI + Pydantic v2での時間関連バリデーション
"""

from datetime import date, time, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class DayOfWeekEnum(int, Enum):
    """曜日の列挙型 (ISO 8601準拠)"""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class NoSendSettingTypeEnum(str, Enum):
    """送信禁止設定の種類"""

    DAY_OF_WEEK = "day_of_week"
    TIME_RANGE = "time_range"
    SPECIFIC_DATE = "specific_date"


# ベーススキーマ
class NoSendSettingBase(BaseModel):
    """送信禁止設定の基底スキーマ"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="設定名",
        examples=["休日送信禁止", "夜間送信禁止"],
    )

    description: str | None = Field(
        None,
        description="設定の説明",
        examples=["土日祝日の送信を禁止します"],
    )

    is_enabled: bool = Field(
        True,
        description="設定の有効/無効",
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """設定名をサニタイズ - 制御文字を削除し、スペースを正規化"""
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("設定名は空にできません")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """説明をサニタイズ - 制御文字を削除（タブと改行は許可）"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


# 曜日設定スキーマ
class NoSendSettingDayOfWeekCreate(NoSendSettingBase):
    """曜日ベースの送信禁止設定（作成用）"""

    setting_type: NoSendSettingTypeEnum = Field(
        NoSendSettingTypeEnum.DAY_OF_WEEK,
        description="設定種別",
    )

    day_of_week_list: list[DayOfWeekEnum] = Field(
        ...,
        min_length=1,
        max_length=7,
        description="送信禁止曜日リスト",
        examples=[[6, 7]],  # 土日
    )

    @field_validator("day_of_week_list")
    @classmethod
    def validate_day_of_week_list(
        cls, v: list[DayOfWeekEnum]
    ) -> list[DayOfWeekEnum]:
        """曜日リストの重複を排除"""
        unique_days = list(set(v))
        unique_days.sort()
        return unique_days


# 時間帯設定スキーマ
class NoSendSettingTimeRangeCreate(NoSendSettingBase):
    """時間帯ベースの送信禁止設定（作成用）"""

    setting_type: NoSendSettingTypeEnum = Field(
        NoSendSettingTypeEnum.TIME_RANGE,
        description="設定種別",
    )

    time_start: time = Field(
        ...,
        description="送信禁止開始時刻 (ISO 8601: HH:MM:SS)",
        examples=["22:00:00"],
    )

    time_end: time = Field(
        ...,
        description="送信禁止終了時刻 (ISO 8601: HH:MM:SS)",
        examples=["08:00:00"],
    )


# 日付設定スキーマ
class NoSendSettingSpecificDateCreate(NoSendSettingBase):
    """特定日付の送信禁止設定（作成用）"""

    setting_type: NoSendSettingTypeEnum = Field(
        NoSendSettingTypeEnum.SPECIFIC_DATE,
        description="設定種別",
    )

    specific_date: date | None = Field(
        None,
        description="送信禁止日 (ISO 8601: YYYY-MM-DD)",
        examples=["2025-01-01"],
    )

    date_range_start: date | None = Field(
        None,
        description="送信禁止期間開始日",
        examples=["2025-12-29"],
    )

    date_range_end: date | None = Field(
        None,
        description="送信禁止期間終了日",
        examples=["2026-01-03"],
    )

    @model_validator(mode="after")
    def validate_date_fields(self):
        """日付フィールドの整合性検証"""
        has_specific = self.specific_date is not None
        has_range = (
            self.date_range_start is not None or self.date_range_end is not None
        )

        # specific_dateとdate_rangeは排他的
        if has_specific and has_range:
            raise ValueError(
                "specific_dateとdate_range_start/endは同時に指定できません"
            )

        # どちらか一方は必須
        if not has_specific and not has_range:
            raise ValueError(
                "specific_dateまたはdate_range_start/endのいずれかが必要です"
            )

        # 範囲指定の場合、両方必須
        if has_range:
            if self.date_range_start is None or self.date_range_end is None:
                raise ValueError(
                    "date_range_startとdate_range_endは両方指定する必要があります"
                )

            # 開始日 <= 終了日
            if self.date_range_start > self.date_range_end:
                raise ValueError(
                    f"開始日（{self.date_range_start}）は終了日（{self.date_range_end}）"
                    "より前である必要があります"
                )

        return self


# 更新用スキーマ
class NoSendSettingUpdateRequest(BaseModel):
    """送信禁止設定更新リクエスト"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="設定名",
    )

    description: str | None = Field(
        None,
        description="設定の説明",
    )

    is_enabled: bool | None = Field(
        None,
        description="設定の有効/無効",
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """設定名をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("設定名は空にできません")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """説明をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


# レスポンススキーマ
class NoSendSettingResponse(BaseModel):
    """送信禁止設定レスポンス"""

    id: int = Field(..., description="設定ID")
    list_id: int = Field(..., description="リストID")
    setting_type: NoSendSettingTypeEnum = Field(..., description="設定種別")
    name: str = Field(..., description="設定名")
    description: str | None = Field(None, description="設定の説明")
    is_enabled: bool = Field(..., description="有効/無効")

    # Optional fields (設定種別によって使用)
    day_of_week_list: list[int] | None = None
    time_start: time | None = None
    time_end: time | None = None
    specific_date: date | None = None
    date_range_start: date | None = None
    date_range_end: date | None = None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "list_id": 10,
                "setting_type": "day_of_week",
                "name": "休日送信禁止",
                "description": "土日の送信を禁止",
                "is_enabled": True,
                "day_of_week_list": [6, 7],
                "time_start": None,
                "time_end": None,
                "specific_date": None,
                "date_range_start": None,
                "date_range_end": None,
                "created_at": "2025-11-19T10:00:00Z",
                "updated_at": "2025-11-19T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class NoSendSettingListResponse(BaseModel):
    """送信禁止設定コレクションレスポンス"""

    settings: list[NoSendSettingResponse] = Field(
        ..., description="送信禁止設定の配列"
    )
    total: int = Field(..., description="総数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "settings": [
                    {
                        "id": 1,
                        "list_id": 10,
                        "setting_type": "day_of_week",
                        "name": "休日送信禁止",
                        "description": "土日の送信を禁止",
                        "is_enabled": True,
                        "day_of_week_list": [6, 7],
                        "time_start": None,
                        "time_end": None,
                        "specific_date": None,
                        "date_range_start": None,
                        "date_range_end": None,
                        "created_at": "2025-11-19T10:00:00Z",
                        "updated_at": "2025-11-19T10:00:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
            }
        },
    )
