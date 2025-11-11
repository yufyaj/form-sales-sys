"""
顧客担当者関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ========================================
# 基底スキーマ
# ========================================


class ClientContactBase(BaseModel):
    """顧客担当者スキーマの基底クラス"""

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="氏名",
        examples=["田中一郎"],
    )
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
    email: EmailStr | None = Field(
        None,
        description="メールアドレス",
        examples=["tanaka@example.com"],
    )
    phone: str | None = Field(
        None,
        max_length=50,
        description="電話番号",
        examples=["03-1234-5678"],
    )
    mobile: str | None = Field(
        None,
        max_length=50,
        description="携帯電話番号",
        examples=["090-1234-5678"],
    )
    is_primary: bool = Field(
        False,
        description="主担当フラグ",
    )
    notes: str | None = Field(
        None,
        description="備考",
        examples=["キーパーソン"],
    )

    @field_validator("phone", "mobile")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """電話番号の基本的なバリデーション"""
        if v is None:
            return v

        # ハイフン、スペース、括弧を除去して数字のみにする
        cleaned = "".join(c for c in v if c.isdigit() or c == "+")

        # 最低限の桁数チェック（日本の電話番号は通常10-11桁）
        if len(cleaned) < 10:
            raise ValueError("電話番号は10桁以上である必要があります")

        return v


# ========================================
# リクエストスキーマ
# ========================================


class ClientContactCreateRequest(ClientContactBase):
    """顧客担当者作成リクエスト"""

    client_organization_id: int = Field(
        ...,
        description="顧客組織ID",
    )


class ClientContactUpdateRequest(BaseModel):
    """顧客担当者更新リクエスト（部分更新対応）"""

    full_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="氏名",
    )
    department: str | None = Field(
        None,
        max_length=255,
        description="部署",
    )
    position: str | None = Field(
        None,
        max_length=255,
        description="役職",
    )
    email: EmailStr | None = Field(
        None,
        description="メールアドレス",
    )
    phone: str | None = Field(
        None,
        max_length=50,
        description="電話番号",
    )
    mobile: str | None = Field(
        None,
        max_length=50,
        description="携帯電話番号",
    )
    is_primary: bool | None = Field(
        None,
        description="主担当フラグ",
    )
    notes: str | None = Field(
        None,
        description="備考",
    )

    @field_validator("phone", "mobile")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        """電話番号の基本的なバリデーション"""
        if v is None:
            return v

        cleaned = "".join(c for c in v if c.isdigit() or c == "+")

        if len(cleaned) < 10:
            raise ValueError("電話番号は10桁以上である必要があります")

        return v


# ========================================
# レスポンススキーマ
# ========================================


class ClientContactResponse(ClientContactBase):
    """顧客担当者レスポンス"""

    id: int = Field(..., description="顧客担当者ID")
    client_organization_id: int = Field(..., description="顧客組織ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "client_organization_id": 1,
                "full_name": "田中一郎",
                "department": "営業部",
                "position": "部長",
                "email": "tanaka@example.com",
                "phone": "03-1234-5678",
                "mobile": "090-1234-5678",
                "is_primary": True,
                "notes": "キーパーソン",
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class ClientContactListResponse(BaseModel):
    """顧客担当者一覧レスポンス"""

    client_contacts: list[ClientContactResponse] = Field(
        ..., description="顧客担当者リスト"
    )
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "client_contacts": [
                    {
                        "id": 1,
                        "client_organization_id": 1,
                        "full_name": "田中一郎",
                        "department": "営業部",
                        "position": "部長",
                        "email": "tanaka@example.com",
                        "phone": "03-1234-5678",
                        "mobile": "090-1234-5678",
                        "is_primary": True,
                        "notes": "キーパーソン",
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
