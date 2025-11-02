"""
組織関連のPydanticスキーマ定義

営業支援会社組織と顧客組織の送受信用スキーマ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ========================================
# 基底スキーマ
# ========================================


class OrganizationBase(BaseModel):
    """組織スキーマの基底クラス"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="組織名",
        examples=["株式会社サンプル"],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="組織の説明",
        examples=["営業支援を提供する企業"],
    )


# ========================================
# リクエストスキーマ
# ========================================


class OrganizationCreateRequest(OrganizationBase):
    """組織作成リクエスト"""

    parent_organization_id: UUID | None = Field(
        None,
        description="親組織ID（顧客組織の場合、営業支援会社のIDを指定）",
    )


class OrganizationUpdateRequest(BaseModel):
    """組織更新リクエスト"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="組織名",
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="組織の説明",
    )


# ========================================
# レスポンススキーマ
# ========================================


class OrganizationResponse(OrganizationBase):
    """組織レスポンス"""

    id: UUID = Field(..., description="組織ID")
    parent_organization_id: UUID | None = Field(
        None,
        description="親組織ID",
    )
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "name": "株式会社サンプル",
                "description": "営業支援を提供する企業",
                "parent_organization_id": None,
                "created_at": "2025-11-03T10:00:00Z",
                "updated_at": "2025-11-03T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class OrganizationListResponse(BaseModel):
    """組織一覧レスポンス"""

    organizations: list[OrganizationResponse] = Field(..., description="組織リスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organizations": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440000",
                        "name": "株式会社サンプル",
                        "description": "営業支援を提供する企業",
                        "parent_organization_id": None,
                        "created_at": "2025-11-03T10:00:00Z",
                        "updated_at": "2025-11-03T10:00:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        },
    )
