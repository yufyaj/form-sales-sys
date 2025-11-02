"""
Pytestフィクスチャ設定

テスト用のデータベース、セッション、初期データなどを提供します。
testcontainersを使用して実際のPostgreSQLコンテナでテストを実行します。
"""
import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.infrastructure.persistence.models import Base

@pytest.fixture(scope="function")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    PostgreSQLコンテナのセットアップ

    テスト用の実際のPostgreSQLコンテナを起動します。
    """
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="function")
async def engine(postgres_container: PostgresContainer) -> AsyncGenerator[Any, None]:
    """
    テスト用の非同期エンジン

    PostgreSQLコンテナに接続する非同期エンジンを作成します。
    """
    # asyncpg用のURL形式に変換
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )

    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)

    # テーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # クリーンアップ
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """
    テスト用のデータベースセッション

    各テストケースで独立したトランザクションを提供します。
    テスト終了時にロールバックされます。
    """
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            # テスト終了時に自動的にロールバック
            await session.rollback()


@pytest.fixture
async def seed_roles(db_session: AsyncSession) -> list[Any]:
    """
    テスト用の基本ロールを作成

    営業支援会社、顧客、ワーカーの3つのロールを作成します。
    """
    from src.infrastructure.persistence.models import Role

    roles_data = [
        {"name": "sales_support", "display_name": "営業支援会社", "description": "営業支援を提供する会社の担当者"},
        {"name": "client", "display_name": "顧客", "description": "営業支援を依頼するクライアント企業の担当者"},
        {"name": "worker", "display_name": "ワーカー", "description": "フォーム営業の実務作業者"},
    ]

    roles = []
    for data in roles_data:
        role = Role(**data)
        db_session.add(role)
        roles.append(role)

    await db_session.flush()
    return roles
