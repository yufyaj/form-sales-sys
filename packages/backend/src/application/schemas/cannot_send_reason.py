"""
送信不可理由関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ========================================
# リクエストスキーマ
# ========================================


class CannotSendReasonCreateRequest(BaseModel):
    """送信不可理由作成リクエスト"""

    reason_code: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）",
        examples=["FORM_NOT_FOUND"],
    )
    reason_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="理由名",
        examples=["フォームが見つからない"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="詳細説明",
        examples=["Webページにフォームが存在しない場合"],
    )
    is_active: bool = Field(
        default=True,
        description="有効/無効フラグ",
        examples=[True],
    )


class CannotSendReasonUpdateRequest(BaseModel):
    """送信不可理由更新リクエスト"""

    reason_code: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="理由コード",
        examples=["FORM_NOT_FOUND"],
    )
    reason_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="理由名",
        examples=["フォームが見つからない"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="詳細説明",
        examples=["Webページにフォームが存在しない、またはアクセスできない場合"],
    )
    is_active: bool | None = Field(
        None,
        description="有効/無効フラグ",
        examples=[False],
    )


# ========================================
# レスポンススキーマ
# ========================================


class CannotSendReasonResponse(BaseModel):
    """送信不可理由レスポンス"""

    id: int = Field(..., description="送信不可理由ID")
    reason_code: str = Field(..., description="理由コード")
    reason_name: str = Field(..., description="理由名")
    description: str | None = Field(None, description="詳細説明")
    is_active: bool = Field(..., description="有効/無効フラグ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "reason_code": "FORM_NOT_FOUND",
                "reason_name": "フォームが見つからない",
                "description": "Webページにフォームが存在しない場合",
                "is_active": True,
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-22T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class CannotSendReasonListResponse(BaseModel):
    """送信不可理由一覧レスポンス"""

    reasons: list[CannotSendReasonResponse] = Field(..., description="送信不可理由リスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reasons": [
                    {
                        "id": 1,
                        "reason_code": "FORM_NOT_FOUND",
                        "reason_name": "フォームが見つからない",
                        "description": "Webページにフォームが存在しない場合",
                        "is_active": True,
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-22T10:00:00Z",
                        "deleted_at": None,
                    },
                    {
                        "id": 2,
                        "reason_code": "CAPTCHA_REQUIRED",
                        "reason_name": "CAPTCHA認証が必要",
                        "description": "フォーム送信にCAPTCHA認証が必要な場合",
                        "is_active": True,
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-22T10:00:00Z",
                        "deleted_at": None,
                    },
                ],
                "total": 2,
                "skip": 0,
                "limit": 100,
            }
        },
    )
