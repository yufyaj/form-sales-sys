"""
アプリケーション設定

環境変数から設定を読み込み、アプリケーション全体で使用する設定を提供します。
Pydantic Settingsを使用して型安全な設定管理を実現します。
"""
from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # データベース設定
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT設定
    SECRET_KEY: str
    # 安全なアルゴリズムのみ許可（"none"などの危険なアルゴリズムを防ぐ）
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 環境設定
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # セキュリティ設定
    ENABLE_RATE_LIMITING: bool = True

    # CORS設定
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """SECRET_KEYのバリデーション"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        # 危険なデフォルト値の検出
        dangerous_values = [
            "your-secret-key",
            "change-this",
            "CHANGE_THIS",
            "secret",
            "password",
        ]
        if any(dangerous in v.lower() for dangerous in dangerous_values):
            raise ValueError(
                "SECRET_KEY contains dangerous default value. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """CORS originのリストを組み立て"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: list[str], info) -> list[str]:
        """本番環境でlocalhostを拒否"""
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production":
            for origin in v:
                if "localhost" in origin or "127.0.0.1" in origin:
                    raise ValueError(
                        "Production environment cannot use localhost CORS origins"
                    )
        return v


@lru_cache
def get_settings() -> Settings:
    """
    設定のシングルトンインスタンスを取得

    lru_cacheにより、初回呼び出し時のみインスタンスを生成し、
    以降は同じインスタンスを返します。
    """
    return Settings()
