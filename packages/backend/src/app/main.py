"""
FastAPIアプリケーションのエントリーポイント

アプリケーションの初期化、ミドルウェアの設定、ルーターの登録を行います。
"""
from fastapi import FastAPI, Request
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

# CORSミドルウェアの設定（セキュリティ強化版）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # 具体的に指定
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "X-Request-ID",
    ],  # 必要なヘッダーのみ
    expose_headers=["X-Request-ID"],  # クライアントに公開するヘッダー
    max_age=600,  # プリフライトリクエストのキャッシュ時間（秒）
)

# セキュリティヘッダーミドルウェア
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    セキュリティヘッダーを追加するミドルウェア

    - HSTS: HTTPS強制（本番環境のみ）
    - X-Content-Type-Options: MIMEタイプスニッフィング防止
    - X-Frame-Options: クリックジャッキング防止
    - X-XSS-Protection: XSS攻撃防止
    - Referrer-Policy: リファラー情報の制御
    - CSP: コンテンツセキュリティポリシー（本番環境のみ）
    """
    response = await call_next(request)

    # 本番環境でのみHSTSを有効化（開発環境では問題を起こす可能性がある）
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # CSP（Content Security Policy）本番環境のみ
    if settings.ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

    return response

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
