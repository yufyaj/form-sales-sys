"""
ユーザー関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ========================================
# 基底スキーマ
# ========================================


class UserBase(BaseModel):
    """ユーザースキーマの基底クラス"""

    email: EmailStr = Field(
        ...,
        description="メールアドレス",
        examples=["user@example.com"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="フルネーム",
        examples=["山田太郎"],
    )


# ========================================
# リクエストスキーマ
# ========================================


class UserCreateRequest(UserBase):
    """ユーザー作成リクエスト"""

    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=128,
            description="パスワード（8文字以上、128文字以下）",
            examples=["SecurePassword123!"],
        ),
    ]
    organization_id: int = Field(
        ...,
        description="所属組織ID",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        パスワードの強度をバリデーション

        - 8文字以上
        - 英大文字、英小文字、数字をそれぞれ1文字以上含む
        """
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "パスワードには英大文字、英小文字、数字をそれぞれ1文字以上含める必要があります"
            )

        return v


class UserUpdateRequest(BaseModel):
    """ユーザー更新リクエスト"""

    email: EmailStr | None = Field(
        None,
        description="メールアドレス",
        examples=["newemail@example.com"],
    )
    full_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="フルネーム",
        examples=["山田花子"],
    )
    is_active: bool | None = Field(
        None,
        description="アクティブフラグ（管理者のみ変更可能）",
    )
    is_email_verified: bool | None = Field(
        None,
        description="メール確認済みフラグ（管理者のみ変更可能）",
    )


class PasswordChangeRequest(BaseModel):
    """パスワード変更リクエスト"""

    current_password: str = Field(
        ...,
        description="現在のパスワード",
    )
    new_password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            max_length=128,
            description="新しいパスワード（8文字以上、128文字以下）",
        ),
    ]

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """パスワードの強度をバリデーション"""
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "パスワードには英大文字、英小文字、数字をそれぞれ1文字以上含める必要があります"
            )

        return v


# ========================================
# レスポンススキーマ
# ========================================


class UserResponse(UserBase):
    """ユーザーレスポンス"""

    id: int = Field(..., description="ユーザーID")
    organization_id: int = Field(..., description="所属組織ID")
    is_active: bool = Field(..., description="アクティブフラグ")
    is_email_verified: bool = Field(..., description="メール確認済みフラグ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemyモデルから変換可能にする
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "山田太郎",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "is_email_verified": True,
                "created_at": "2025-11-03T10:00:00Z",
                "updated_at": "2025-11-03T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""

    users: list[UserResponse] = Field(..., description="ユーザーリスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user1@example.com",
                        "full_name": "山田太郎",
                        "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                        "is_active": True,
                        "is_email_verified": True,
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


# ========================================
# ロール関連スキーマ
# ========================================


class RoleResponse(BaseModel):
    """ロールレスポンス"""

    id: int = Field(..., description="ロールID")
    name: str = Field(..., description="ロール名")
    display_name: str = Field(..., description="表示名")
    description: str | None = Field(None, description="説明")

    model_config = ConfigDict(from_attributes=True)


class UserWithRolesResponse(UserResponse):
    """ロール情報を含むユーザーレスポンス"""

    roles: list[RoleResponse] = Field(..., description="割り当てられたロール")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "山田太郎",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "is_email_verified": True,
                "created_at": "2025-11-03T10:00:00Z",
                "updated_at": "2025-11-03T10:00:00Z",
                "deleted_at": None,
                "roles": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440000",
                        "name": "sales_support",
                        "display_name": "営業支援会社",
                        "description": "営業支援会社の担当者",
                    }
                ],
            }
        },
    )


class RoleAssignRequest(BaseModel):
    """ロール割り当てリクエスト"""

    role_id: int = Field(..., description="割り当てるロールID")
