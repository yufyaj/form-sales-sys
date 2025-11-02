"""
FastAPIアプリケーションのエントリーポイント

アプリケーションの初期化、ミドルウェアの設定、ルーターの登録を行います。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api import auth
from src.app.core.config import get_settings

settings = get_settings()

# FastAPIアプリケーションの作成
app = FastAPI(
    title="フォーム営業支援システム API",
    description="営業支援会社、顧客、ワーカーを繋ぐプラットフォームのバックエンドAPI",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,  # 本番環境ではドキュメントを無効化
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth.router)


@app.get("/")
async def root() -> dict:
    """ルートエンドポイント"""
    return {
        "message": "フォーム営業支援システム API",
        "version": "0.1.0",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


@app.get("/health")
async def health_check() -> dict:
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
