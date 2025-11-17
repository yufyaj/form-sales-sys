"""
顧客組織関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ========================================
# 基底スキーマ
# ========================================


class ClientOrganizationBase(BaseModel):
    """顧客組織スキーマの基底クラス"""

    industry: str | None = Field(
        None,
        max_length=255,
        description="業種",
        examples=["IT・ソフトウェア"],
    )
    employee_count: int | None = Field(
        None,
        ge=0,
        description="従業員数",
        examples=[100],
    )
    annual_revenue: int | None = Field(
        None,
        ge=0,
        description="年商（円）",
        examples=[100000000],
    )
    established_year: int | None = Field(
        None,
        ge=1800,
        le=2100,
        description="設立年",
        examples=[2010],
    )
    website: str | None = Field(
        None,
        max_length=500,
        description="Webサイト",
        examples=["https://example.com"],
    )
    sales_person: str | None = Field(
        None,
        max_length=255,
        description="担当営業",
        examples=["山田太郎"],
    )
    notes: str | None = Field(
        None,
        description="備考",
        examples=["重要顧客"],
    )

    @field_validator("website")
    @classmethod
    def validate_website_url(cls, v: str | None) -> str | None:
        """WebサイトURLのバリデーション"""
        if v is None:
            return v

        # URLの基本的なバリデーション
        if not v.startswith(("http://", "https://")):
            raise ValueError("WebサイトURLはhttp://またはhttps://で始まる必要があります")

        return v


# ========================================
# リクエストスキーマ
# ========================================


class ClientOrganizationCreateRequest(ClientOrganizationBase):
    """顧客組織作成リクエスト"""

    organization_id: int = Field(
        ...,
        description="対応するOrganizationのID（1:1関係）",
    )


class ClientOrganizationUpdateRequest(BaseModel):
    """顧客組織更新リクエスト（部分更新対応）"""

    industry: str | None = Field(
        None,
        max_length=255,
        description="業種",
    )
    employee_count: int | None = Field(
        None,
        ge=0,
        description="従業員数",
    )
    annual_revenue: int | None = Field(
        None,
        ge=0,
        description="年商（円）",
    )
    established_year: int | None = Field(
        None,
        ge=1800,
        le=2100,
        description="設立年",
    )
    website: str | None = Field(
        None,
        max_length=500,
        description="Webサイト",
    )
    sales_person: str | None = Field(
        None,
        max_length=255,
        description="担当営業",
    )
    notes: str | None = Field(
        None,
        description="備考",
    )

    @field_validator("website")
    @classmethod
    def validate_website_url(cls, v: str | None) -> str | None:
        """WebサイトURLのバリデーション"""
        if v is None:
            return v

        if not v.startswith(("http://", "https://")):
            raise ValueError("WebサイトURLはhttp://またはhttps://で始まる必要があります")

        return v


# ========================================
# レスポンススキーマ
# ========================================


class ClientOrganizationResponse(ClientOrganizationBase):
    """顧客組織レスポンス"""

    id: int = Field(..., description="顧客組織ID")
    organization_id: int = Field(..., description="対応するOrganizationのID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "organization_id": 100,
                "industry": "IT・ソフトウェア",
                "employee_count": 100,
                "annual_revenue": 100000000,
                "established_year": 2010,
                "website": "https://example.com",
                "sales_person": "山田太郎",
                "notes": "重要顧客",
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class ClientOrganizationListResponse(BaseModel):
    """顧客組織一覧レスポンス"""

    client_organizations: list[ClientOrganizationResponse] = Field(
        ..., description="顧客組織リスト"
    )
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_organizations": [
                    {
                        "id": 1,
                        "organization_id": 100,
                        "industry": "IT・ソフトウェア",
                        "employee_count": 100,
                        "annual_revenue": 100000000,
                        "established_year": 2010,
                        "website": "https://example.com",
                        "sales_person": "山田太郎",
                        "notes": "重要顧客",
                        "created_at": "2025-11-11T10:00:00Z",
                        "updated_at": "2025-11-11T10:00:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 50,
            }
        },
    )
