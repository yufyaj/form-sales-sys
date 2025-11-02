"""
FastAPIアプリケーションのエントリーポイント

アプリケーションの初期化、ルーター登録、グローバル設定を行います
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as users_router
from app.core.config import get_settings
from app.core.exceptions import domain_exception_handler
from domain.exceptions import DomainException

settings = get_settings()

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="フォーム営業支援システム API",
    description="営業支援会社、顧客、ワーカーを管理するバックエンドAPI",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # 本番環境ではSwagger UIを無効化
    redoc_url="/redoc" if settings.DEBUG else None,  # 本番環境ではReDocを無効化
)

# CORS設定
# 本番環境では適切なオリジンのみを許可すること
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル例外ハンドラーの登録
# ドメイン層の例外を適切なHTTPレスポンスに変換
app.add_exception_handler(DomainException, domain_exception_handler)

# ルーターの登録
app.include_router(users_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    ヘルスチェックエンドポイント

    アプリケーションの稼働状態を確認します
    """
    return {"status": "healthy"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    ルートエンドポイント

    APIの基本情報を返します
    """
    return {
        "message": "フォーム営業支援システム API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }
