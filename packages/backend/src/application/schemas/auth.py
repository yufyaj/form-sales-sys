"""
認証関連のスキーマ

ログイン、トークン、認証ユーザー情報のPydanticモデルを定義します
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    ログインリクエスト

    メールアドレスとパスワードでユーザー認証を行います
    """

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=1, description="パスワード")

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com", "password": "SecurePass123"}}}


class TokenResponse(BaseModel):
    """
    トークンレスポンス

    JWTアクセストークンとトークンタイプを返します
    """

    access_token: str = Field(..., description="JWTアクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")

    model_config = {"json_schema_extra": {"example": {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}}}


class TokenPayload(BaseModel):
    """
    JWTトークンペイロード

    トークンに含まれるユーザー情報
    """

    sub: int = Field(..., description="ユーザーID（subject）")
    organization_id: int = Field(..., description="組織ID")
    email: str = Field(..., description="メールアドレス")
    exp: int = Field(..., description="有効期限（UNIX timestamp）")

    model_config = {"json_schema_extra": {"example": {"sub": 1, "organization_id": 1, "email": "user@example.com", "exp": 1735689600}}}


class CurrentUser(BaseModel):
    """
    認証済みユーザー情報

    get_current_user依存性から返される現在のユーザー情報
    """

    id: int = Field(..., description="ユーザーID")
    email: str = Field(..., description="メールアドレス")
    organization_id: int = Field(..., description="組織ID")
    full_name: str = Field(..., description="氏名")
    is_active: bool = Field(..., description="アクティブ状態")

    model_config = {"json_schema_extra": {"example": {"id": 1, "email": "user@example.com", "organization_id": 1, "full_name": "山田太郎", "is_active": True}}}
