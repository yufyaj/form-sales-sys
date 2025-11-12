"""
営業支援会社担当者関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ========================================
# 基底スキーマ
# ========================================


class SalesCompanyStaffBase(BaseModel):
    """営業支援会社担当者スキーマの基底クラス"""

    department: str | None = Field(
        None,
        max_length=255,
        description="部署",
        examples=["営業部"],
    )
    position: str | None = Field(
        None,
        max_length=255,
        description="役職",
        examples=["課長"],
    )
    employee_number: str | None = Field(
        None,
        max_length=100,
        description="社員番号",
        examples=["EMP-001"],
    )
    notes: str | None = Field(
        None,
        description="備考",
        examples=["新入社員"],
    )


# ========================================
# リクエストスキーマ
# ========================================


class SalesCompanyStaffCreateRequest(SalesCompanyStaffBase):
    """営業支援会社担当者作成リクエスト"""

    user_id: int = Field(
        ...,
        description="ユーザーID（対応するUserレコードのID）",
        examples=[1],
    )


class SalesCompanyStaffUpdateRequest(BaseModel):
    """営業支援会社担当者更新リクエスト"""

    department: str | None = Field(
        None,
        max_length=255,
        description="部署",
        examples=["営業部"],
    )
    position: str | None = Field(
        None,
        max_length=255,
        description="役職",
        examples=["部長"],
    )
    employee_number: str | None = Field(
        None,
        max_length=100,
        description="社員番号",
        examples=["EMP-001"],
    )
    notes: str | None = Field(
        None,
        description="備考",
        examples=["昇進"],
    )


# ========================================
# レスポンススキーマ
# ========================================


class SalesCompanyStaffResponse(SalesCompanyStaffBase):
    """営業支援会社担当者レスポンス"""

    id: int = Field(..., description="営業支援会社担当者ID")
    user_id: int = Field(..., description="ユーザーID")
    organization_id: int = Field(..., description="所属組織ID（営業支援会社）")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemyモデルから変換可能にする
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "organization_id": 1,
                "department": "営業部",
                "position": "課長",
                "employee_number": "EMP-001",
                "notes": "営業担当",
                "created_at": "2025-11-12T10:00:00Z",
                "updated_at": "2025-11-12T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class SalesCompanyStaffListResponse(BaseModel):
    """営業支援会社担当者一覧レスポンス"""

    staff: list[SalesCompanyStaffResponse] = Field(..., description="担当者リスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "staff": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "organization_id": 1,
                        "department": "営業部",
                        "position": "課長",
                        "employee_number": "EMP-001",
                        "notes": "営業担当",
                        "created_at": "2025-11-12T10:00:00Z",
                        "updated_at": "2025-11-12T10:00:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        },
    )


# ========================================
# ユーザー情報を含むレスポンス
# ========================================


class SalesCompanyStaffWithUserResponse(SalesCompanyStaffResponse):
    """ユーザー情報を含む営業支援会社担当者レスポンス"""

    user_email: str = Field(..., description="ユーザーメールアドレス")
    user_full_name: str = Field(..., description="ユーザー氏名")
    user_phone: str | None = Field(None, description="ユーザー電話番号")
    user_is_active: bool = Field(..., description="ユーザーアクティブフラグ")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "organization_id": 1,
                "department": "営業部",
                "position": "課長",
                "employee_number": "EMP-001",
                "notes": "営業担当",
                "user_email": "staff@example.com",
                "user_full_name": "山田太郎",
                "user_phone": "090-1234-5678",
                "user_is_active": True,
                "created_at": "2025-11-12T10:00:00Z",
                "updated_at": "2025-11-12T10:00:00Z",
                "deleted_at": None,
            }
        },
    )
