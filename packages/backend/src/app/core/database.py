"""
データベース接続とセッション管理

SQLAlchemy 2.0の非同期接続を使用したデータベースセッション管理を提供します。
"""
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings

settings = get_settings()

# 非同期エンジンの作成
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # 接続の健全性チェック
)

# セッションファクトリの作成
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    データベースセッションの依存性注入用関数

    FastAPIのDependsで使用します。
    セッションの自動クローズとエラーハンドリングを行います。

    使用例:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    データベースの初期化

    開発環境でのみ使用します。
    本番環境ではAlembicマイグレーションを使用してください。
    """
    from src.infrastructure.persistence.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """データベース接続のクローズ"""
    await engine.dispose()
