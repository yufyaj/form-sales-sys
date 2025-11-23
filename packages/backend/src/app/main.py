"""
FastAPIアプリケーションのエントリーポイント

アプリケーションの初期化、ミドルウェアの設定、ルーター登録、グローバル設定を行います
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.app.api import auth
from src.app.api.cannot_send_reasons import router as cannot_send_reasons_router
from src.app.api.client_contacts import router as client_contacts_router
from src.app.api.client_organizations import router as client_organizations_router
from src.app.api.csv_import import router as csv_import_router
from src.app.api.list_item_assignments import router as list_item_assignments_router
from src.app.api.list_items import router as list_items_router
from src.app.api.list_scripts import router as list_scripts_router
from src.app.api.lists import router as lists_router
from src.app.api.ng_list_domains import router as ng_list_domains_router
from src.app.api.no_send_settings import router as no_send_settings_router
from src.app.api.projects import router as projects_router
from src.app.api.sales_company_staff import router as sales_company_staff_router
from src.app.api.users import router as users_router
from src.app.api.worker_questions import router as worker_questions_router
from src.app.api.workers import router as workers_router
from src.app.api.work_records import router as work_records_router
from src.app.api.worker_assignments import router as worker_assignments_router
from src.app.core.config import get_settings
from src.app.core.exceptions import domain_exception_handler
from src.domain.exceptions import DomainException

settings = get_settings()

# レート制限の初期化
# IPアドレスベースでリクエスト数を制限（DoS攻撃対策）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour"],  # デフォルト: 1分あたり100回、1時間あたり1000回
)

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="フォーム営業支援システム API",
    description="営業支援会社、顧客、ワーカーを管理するバックエンドAPI",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # 本番環境ではSwagger UIを無効化
    redoc_url="/redoc" if settings.DEBUG else None,  # 本番環境ではReDocを無効化
)

# レート制限をアプリケーションに登録
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS設定（セキュリティ強化版）
# 本番環境では適切なオリジンのみを許可すること
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


# グローバル例外ハンドラーの登録
# ドメイン層の例外を適切なHTTPレスポンスに変換
app.add_exception_handler(DomainException, domain_exception_handler)

# ルーターの登録
app.include_router(auth.router)  # 認証ルーターは /auth をプレフィックスとして持つ
app.include_router(users_router, prefix="/api/v1")  # ユーザー管理は /api/v1/users
app.include_router(
    sales_company_staff_router, prefix="/api/v1"
)  # 営業支援会社担当者は /api/v1/sales-company-staff
app.include_router(
    client_organizations_router, prefix="/api/v1"
)  # 顧客組織管理は /api/v1/client-organizations
app.include_router(
    client_contacts_router, prefix="/api/v1"
)  # 顧客担当者管理は /api/v1/client-contacts
app.include_router(projects_router, prefix="/api/v1")  # プロジェクト管理は /api/v1/projects
app.include_router(lists_router, prefix="/api/v1")  # リスト管理は /api/v1/lists
app.include_router(
    list_scripts_router, prefix="/api/v1"
)  # リストスクリプト管理は /api/v1/list-scripts
app.include_router(
    ng_list_domains_router, prefix="/api/v1"
)  # NGリスト管理は /api/v1/ng-list-domains
app.include_router(csv_import_router, prefix="/api/v1")  # CSVインポートは /api/v1/csv-import
app.include_router(
    no_send_settings_router, prefix="/api/v1"
)  # 送信禁止設定は /api/v1/no-send-settings
app.include_router(
    cannot_send_reasons_router, prefix="/api/v1"
)  # 送信不可理由管理は /api/v1/cannot-send-reasons
app.include_router(workers_router, prefix="/api/v1")  # ワーカー管理は /api/v1/workers
app.include_router(
    list_item_assignments_router, prefix="/api/v1"
)  # リスト項目割り当ては /api/v1/lists/{list_id}/assign-workers
app.include_router(
    list_items_router, prefix="/api/v1"
)  # リスト項目管理は /api/v1/list-items
app.include_router(
    worker_questions_router, prefix="/api/v1"
)  # ワーカー質問管理は /api/v1/worker-questions
app.include_router(
    work_records_router, prefix="/api/v1"
)  # 作業記録は /api/v1/work-records
app.include_router(
    worker_assignments_router, prefix="/api/v1"
)  # ワーカー割り当ては /api/v1/workers/{worker_id}/assignments


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
