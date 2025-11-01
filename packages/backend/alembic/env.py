"""
Alembic環境設定

SQLAlchemy 2.0とasyncpgを使用した非同期マイグレーション設定です。
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config オブジェクト
config = context.config

# Pythonロギング設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# モデルのメタデータをインポート
from src.infrastructure.persistence.models import Base

target_metadata = Base.metadata

# その他の値をAlembic configから取得
# （例: my_important_option = config.get_main_option("my_important_option")）


def run_migrations_offline() -> None:
    """
    オフラインモードでのマイグレーション実行

    データベースに接続せずにSQLを生成します。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """マイグレーションを実行"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """非同期マイグレーションの実行"""
    # .envファイルから設定を読み込む
    from src.app.core.config import get_settings

    settings = get_settings()

    # Alembic設定を上書き
    config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

    # 非同期エンジンを作成
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    オンラインモードでのマイグレーション実行

    実際のデータベースに接続してマイグレーションを実行します。
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
