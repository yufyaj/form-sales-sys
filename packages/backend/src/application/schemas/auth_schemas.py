"""
認証関連のスキーマ

API送受信用のDTO（Data Transfer Object）を定義します。
Pydanticモデルでバリデーションを行います。
"""
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """ユーザー登録リクエスト"""

    organization_id: int = Field(..., gt=0, description="所属組織ID")
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, max_length=72, description="パスワード（8-72文字）")
    full_name: str = Field(..., min_length=1, max_length=255, description="氏名")
    phone: str | None = Field(None, max_length=50, description="電話番号")
    avatar_url: str | None = Field(None, max_length=500, description="プロフィール画像URL")
    description: str | None = Field(None, description="備考")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        パスワードの強度をバリデーション

        最低限の要件：
        - 8文字以上、72文字以下（bcryptの制限）
        - 英字と数字を含む
        - UTF-8エンコード時に72バイト以下
        """
        # bcryptの制限（72バイト）をチェック
        if len(v.encode("utf-8")) > 72:
            raise ValueError("パスワードは72バイト以下にする必要があります")

        if not any(c.isalpha() for c in v):
            raise ValueError("パスワードには英字を含める必要があります")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードには数字を含める必要があります")
        return v


class UserLoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")


class TokenResponse(BaseModel):
    """トークンレスポンス"""

    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")


class UserResponse(BaseModel):
    """ユーザーレスポンス"""

    id: int
    organization_id: int
    email: str
    full_name: str
    phone: str | None
    avatar_url: str | None
    description: str | None
    is_active: bool
    is_email_verified: bool

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """パスワードリセットリクエスト（リセットトークンを使用）"""

    token: str = Field(..., description="パスワードリセットトークン")
    new_password: str = Field(..., min_length=8, max_length=72, description="新しいパスワード（8-72文字）")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        パスワードの強度をバリデーション

        最低限の要件：
        - 8文字以上、72文字以下（bcryptの制限）
        - 英字と数字を含む
        - UTF-8エンコード時に72バイト以下
        """
        # bcryptの制限（72バイト）をチェック
        if len(v.encode("utf-8")) > 72:
            raise ValueError("パスワードは72バイト以下にする必要があります")

        if not any(c.isalpha() for c in v):
            raise ValueError("パスワードには英字を含める必要があります")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードには数字を含める必要があります")
        return v


class PasswordResetRequestEmail(BaseModel):
    """パスワードリセット依頼（メールアドレス指定）"""

    email: EmailStr = Field(..., description="メールアドレス")
