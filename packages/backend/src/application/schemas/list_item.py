"""
リスト項目関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ========================================
# リクエストスキーマ
# ========================================


class ListItemUpdateRequest(BaseModel):
    """
    リスト項目更新リクエスト（会社名以外のフィールド）

    会社名（title）は企業の一意性を保証する重要なフィールドのため、
    このエンドポイントでは変更できません。
    """

    status: str | None = Field(
        None,
        description="ステータス（pending, contacted, negotiating, closed_won, closed_lost, on_hold）",
        examples=["contacted"],
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """ステータスの妥当性を検証"""
        if v is None:
            return None

        # 許可されたステータス値
        allowed_statuses = {
            "pending",
            "contacted",
            "negotiating",
            "closed_won",
            "closed_lost",
            "on_hold",
        }

        if v not in allowed_statuses:
            raise ValueError(
                f"Invalid status. Allowed values: {', '.join(sorted(allowed_statuses))}"
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "contacted",
            }
        },
    )


class ListItemStatusUpdateRequest(BaseModel):
    """
    リスト項目ステータス更新リクエスト

    ステータスのみを更新する専用エンドポイント用
    """

    status: str = Field(
        ...,
        description="ステータス（pending, contacted, negotiating, closed_won, closed_lost, on_hold）",
        examples=["negotiating"],
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """ステータスの妥当性を検証"""
        # 許可されたステータス値
        allowed_statuses = {
            "pending",
            "contacted",
            "negotiating",
            "closed_won",
            "closed_lost",
            "on_hold",
        }

        if v not in allowed_statuses:
            raise ValueError(
                f"Invalid status. Allowed values: {', '.join(sorted(allowed_statuses))}"
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "negotiating",
            }
        },
    )


# ========================================
# レスポンススキーマ
# ========================================


class ListItemResponse(BaseModel):
    """リスト項目レスポンス"""

    id: int = Field(..., description="リスト項目ID")
    list_id: int = Field(..., description="リストID")
    title: str = Field(..., description="企業名などのタイトル")
    status: str = Field(..., description="ステータス")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "list_id": 10,
                "title": "株式会社サンプル",
                "status": "contacted",
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-23T15:30:00Z",
                "deleted_at": None,
            }
        },
    )


class ListItemListResponse(BaseModel):
    """リスト項目一覧レスポンス"""

    items: list[ListItemResponse] = Field(..., description="リスト項目配列")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "list_id": 10,
                        "title": "株式会社サンプル",
                        "status": "contacted",
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-23T15:30:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        },
    )
