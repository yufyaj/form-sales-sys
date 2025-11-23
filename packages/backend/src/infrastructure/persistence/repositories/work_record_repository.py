"""
作業記録リポジトリの実装

IWorkRecordRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.work_record_entity import WorkRecordEntity
from src.domain.exceptions import WorkRecordNotFoundError
from src.domain.interfaces.work_record_repository import IWorkRecordRepository
from src.infrastructure.persistence.models.work_record import WorkRecord, WorkRecordStatus
from src.infrastructure.persistence.models.worker import Worker

# セキュリティログ用のロガー
logger = logging.getLogger(__name__)


def _sanitize_submission_result_for_logging(result: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    ログ記録用に送信結果を無害化（機密情報を除去）

    機密情報の可能性があるフィールドをマスクし、
    セキュリティログに機密データが記録されないようにします。

    Args:
        result: 送信結果の辞書

    Returns:
        サニタイズされた辞書、またはNone
    """
    if result is None:
        return None

    # 機密情報の可能性があるキーのセット
    sensitive_keys = {
        "password", "passwd", "pwd",
        "token", "access_token", "refresh_token", "bearer",
        "api_key", "apikey", "secret", "private_key",
        "authorization", "auth",
        "cookie", "session", "session_id",
        "credit_card", "card_number", "cvv", "cvc",
        "ssn", "social_security",
    }

    sanitized = {}
    for key, value in result.items():
        key_lower = key.lower()

        # キー名に機密情報を示す文字列が含まれている場合はマスク
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        # 長い文字列は省略（バイナリデータやbase64エンコードされたデータ等）
        elif isinstance(value, str) and len(value) > 200:
            sanitized[key] = f"{value[:50]}... (truncated, length: {len(value)})"
        # ネストされた辞書は再帰的にサニタイズ
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_submission_result_for_logging(value)
        else:
            sanitized[key] = value

    return sanitized


class WorkRecordRepository(IWorkRecordRepository):
    """
    作業記録リポジトリの実装

    SQLAlchemyを使用して作業記録の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        assignment_id: int,
        worker_id: int,
        status: WorkRecordStatus,
        started_at: datetime,
        completed_at: datetime,
        form_submission_result: dict[str, Any] | None = None,
        cannot_send_reason_id: int | None = None,
        notes: str | None = None,
    ) -> WorkRecordEntity:
        """作業記録を作成"""
        record = WorkRecord(
            assignment_id=assignment_id,
            worker_id=worker_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            form_submission_result=form_submission_result,
            cannot_send_reason_id=cannot_send_reason_id,
            notes=notes,
        )

        self._session.add(record)
        await self._session.flush()
        await self._session.refresh(record)

        # 作業時間を計算
        duration_minutes = int((completed_at - started_at).total_seconds() / 60)

        logger.info(
            "Work record created successfully",
            extra={
                "event_type": "work_record_created",
                "record_id": record.id,
                "assignment_id": assignment_id,
                "worker_id": worker_id,
                "status": status.value,
                "duration_minutes": duration_minutes,
                "cannot_send_reason_id": cannot_send_reason_id,
                # 機密情報を除外した送信結果をログに記録
                "form_submission_result": _sanitize_submission_result_for_logging(form_submission_result),
            },
        )

        return self._to_entity(record)

    async def find_by_id(
        self,
        record_id: int,
    ) -> WorkRecordEntity | None:
        """IDで作業記録を検索"""
        stmt = select(WorkRecord).where(
            WorkRecord.id == record_id,
            WorkRecord.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()

        return self._to_entity(record) if record else None

    async def find_by_assignment_id(
        self,
        assignment_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """割り当てIDで作業記録を検索"""
        conditions = [WorkRecord.assignment_id == assignment_id]

        if not include_deleted:
            conditions.append(WorkRecord.deleted_at.is_(None))

        stmt = (
            select(WorkRecord)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(WorkRecord.completed_at.desc())
        )

        result = await self._session.execute(stmt)
        record_list = result.scalars().all()

        return [self._to_entity(r) for r in record_list]

    async def find_by_worker_id(
        self,
        worker_id: int,
        status: WorkRecordStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """ワーカーIDで作業記録を検索"""
        conditions = [WorkRecord.worker_id == worker_id]

        if status is not None:
            conditions.append(WorkRecord.status == status)
        if start_date is not None:
            conditions.append(WorkRecord.completed_at >= start_date)
        if end_date is not None:
            conditions.append(WorkRecord.completed_at <= end_date)
        if not include_deleted:
            conditions.append(WorkRecord.deleted_at.is_(None))

        stmt = (
            select(WorkRecord)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(WorkRecord.completed_at.desc())
        )

        result = await self._session.execute(stmt)
        record_list = result.scalars().all()

        return [self._to_entity(r) for r in record_list]

    async def count_by_worker_id(
        self,
        worker_id: int,
        status: WorkRecordStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """ワーカーIDで作業記録の件数をカウント"""
        conditions = [WorkRecord.worker_id == worker_id]

        if status is not None:
            conditions.append(WorkRecord.status == status)
        if start_date is not None:
            conditions.append(WorkRecord.completed_at >= start_date)
        if end_date is not None:
            conditions.append(WorkRecord.completed_at <= end_date)
        if not include_deleted:
            conditions.append(WorkRecord.deleted_at.is_(None))

        stmt = (
            select(func.count())
            .select_from(WorkRecord)
            .where(and_(*conditions))
        )

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def list_by_status(
        self,
        status: WorkRecordStatus,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """ステータスで作業記録を検索"""
        conditions = [WorkRecord.status == status]

        if start_date is not None:
            conditions.append(WorkRecord.completed_at >= start_date)
        if end_date is not None:
            conditions.append(WorkRecord.completed_at <= end_date)
        if not include_deleted:
            conditions.append(WorkRecord.deleted_at.is_(None))

        stmt = (
            select(WorkRecord)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(WorkRecord.completed_at.desc())
        )

        result = await self._session.execute(stmt)
        record_list = result.scalars().all()

        return [self._to_entity(r) for r in record_list]

    async def update(
        self,
        record: WorkRecordEntity,
    ) -> WorkRecordEntity:
        """作業記録を更新"""
        stmt = select(WorkRecord).where(
            WorkRecord.id == record.id,
            WorkRecord.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_record = result.scalar_one_or_none()

        if db_record is None:
            raise WorkRecordNotFoundError(record.id)

        # 更新前の値を保存（監査ログ用）
        old_values = {
            "status": db_record.status.value,
            "cannot_send_reason_id": db_record.cannot_send_reason_id,
        }

        # エンティティの値でモデルを更新
        db_record.status = record.status
        db_record.started_at = record.started_at
        db_record.completed_at = record.completed_at
        db_record.form_submission_result = record.form_submission_result
        db_record.cannot_send_reason_id = record.cannot_send_reason_id
        db_record.notes = record.notes

        await self._session.flush()
        await self._session.refresh(db_record)

        logger.info(
            "Work record updated successfully",
            extra={
                "event_type": "work_record_updated",
                "record_id": record.id,
                "worker_id": record.worker_id,
                "old_values": old_values,
                "new_values": {
                    "status": record.status.value,
                    "cannot_send_reason_id": record.cannot_send_reason_id,
                },
            },
        )

        return self._to_entity(db_record)

    async def soft_delete(
        self,
        record_id: int,
    ) -> None:
        """作業記録を論理削除（ソフトデリート）"""
        stmt = select(WorkRecord).where(
            WorkRecord.id == record_id,
            WorkRecord.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()

        if record is None:
            raise WorkRecordNotFoundError(record_id)

        record.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        logger.info(
            "Work record soft deleted successfully",
            extra={
                "event_type": "work_record_deleted",
                "record_id": record_id,
                "worker_id": record.worker_id,
                "assignment_id": record.assignment_id,
            },
        )

    async def find_by_id_with_access_check(
        self,
        record_id: int,
        requesting_worker_id: int,
        requesting_organization_id: int,
    ) -> WorkRecordEntity | None:
        """
        IDで作業記録を検索（アクセス権限チェック付き）

        マルチテナント環境でのIDOR脆弱性対策。
        同じ組織のワーカーのみアクセス可能。
        """
        stmt = (
            select(WorkRecord)
            .join(Worker, WorkRecord.worker_id == Worker.id)
            .where(
                WorkRecord.id == record_id,
                WorkRecord.deleted_at.is_(None),
                # 同じ組織のワーカーのみアクセス可能
                Worker.organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        record = result.scalar_one_or_none()

        if record is None:
            # データが存在しないのか権限がないのかを区別しない（セキュリティ）
            logger.warning(
                "Work record access denied or not found",
                extra={
                    "event_type": "work_record_access_denied",
                    "record_id": record_id,
                    "requesting_worker_id": requesting_worker_id,
                    "requesting_organization_id": requesting_organization_id,
                },
            )
            return None

        logger.info(
            "Work record accessed successfully with permission check",
            extra={
                "event_type": "work_record_accessed",
                "record_id": record_id,
                "requesting_worker_id": requesting_worker_id,
                "requesting_organization_id": requesting_organization_id,
            },
        )

        return self._to_entity(record)

    def _to_entity(self, record: WorkRecord) -> WorkRecordEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return WorkRecordEntity(
            id=record.id,
            assignment_id=record.assignment_id,
            worker_id=record.worker_id,
            status=record.status,
            started_at=record.started_at,
            completed_at=record.completed_at,
            form_submission_result=record.form_submission_result,
            cannot_send_reason_id=record.cannot_send_reason_id,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
            deleted_at=record.deleted_at,
        )
