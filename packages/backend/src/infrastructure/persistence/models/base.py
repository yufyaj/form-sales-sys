"""
データベースモデルの基底クラス

SQLAlchemy 2.0の型ヒントとマルチテナント対応の共通機能を提供します。
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """すべてのモデルの基底クラス"""

    pass


class TimestampMixin:
    """作成日時・更新日時を管理するMixin"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """論理削除を管理するMixin"""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        """削除済みかどうかを判定"""
        return self.deleted_at is not None
