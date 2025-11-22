"""
ワーカーリポジトリの実装

IWorkerRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.worker_entity import WorkerEntity
from src.domain.exceptions import WorkerNotFoundError
from src.domain.interfaces.worker_repository import IWorkerRepository
from src.infrastructure.persistence.models.worker import SkillLevel, Worker, WorkerStatus

# セキュリティログ用のロガー
logger = logging.getLogger(__name__)


class WorkerRepository(IWorkerRepository):
    """
    ワーカーリポジトリの実装

    SQLAlchemyを使用してワーカーの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        user_id: int,
        organization_id: int,
        status: WorkerStatus = WorkerStatus.PENDING,
        skill_level: SkillLevel | None = None,
        experience_months: int | None = None,
        specialties: str | None = None,
        max_tasks_per_day: int | None = None,
        available_hours_per_week: int | None = None,
        notes: str | None = None,
    ) -> WorkerEntity:
        """ワーカーを作成"""
        worker = Worker(
            user_id=user_id,
            organization_id=organization_id,
            status=status,
            skill_level=skill_level,
            experience_months=experience_months,
            specialties=specialties,
            max_tasks_per_day=max_tasks_per_day,
            available_hours_per_week=available_hours_per_week,
            notes=notes,
        )

        self._session.add(worker)
        await self._session.flush()
        await self._session.refresh(worker)

        # セキュリティログ: ワーカー作成成功
        logger.info(
            "Worker created successfully",
            extra={
                "event_type": "worker_created",
                "worker_id": worker.id,
                "user_id": user_id,
                "organization_id": organization_id,
                "status": status.value,
                "skill_level": skill_level.value if skill_level else None,
            },
        )

        return self._to_entity(worker)

    async def find_by_id(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> WorkerEntity | None:
        """IDでワーカーを検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Worker).where(
            Worker.id == worker_id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        worker = result.scalar_one_or_none()

        # IDOR攻撃検出ログ
        if worker is None:
            # 実際にワーカーが存在するか確認（IDOR試行の検出）
            check_stmt = select(Worker).where(
                Worker.id == worker_id,
                Worker.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_worker = check_result.scalar_one_or_none()

            if actual_worker is not None:
                # ワーカーは存在するが、別組織からのアクセス試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant access attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_access",
                        "worker_id": worker_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_worker.organization_id,
                    },
                )

        return self._to_entity(worker) if worker else None

    async def find_by_user_id(
        self,
        user_id: int,
        requesting_organization_id: int,
    ) -> WorkerEntity | None:
        """ユーザーIDでワーカーを検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Worker).where(
            Worker.user_id == user_id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        worker = result.scalar_one_or_none()

        if worker is None:
            return None

        return self._to_entity(worker)

    async def list_by_organization(
        self,
        organization_id: int,
        status: WorkerStatus | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkerEntity]:
        """営業支援会社に属するワーカーの一覧を取得"""
        conditions = [
            Worker.organization_id == organization_id,
        ]
        if status is not None:
            conditions.append(Worker.status == status)
        if not include_deleted:
            conditions.append(Worker.deleted_at.is_(None))

        stmt = (
            select(Worker)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Worker.created_at.desc())
        )

        result = await self._session.execute(stmt)
        worker_list = result.scalars().all()

        return [self._to_entity(w) for w in worker_list]

    async def count_by_organization(
        self,
        organization_id: int,
        status: WorkerStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """営業支援会社に属するワーカーの総件数を取得"""
        conditions = [
            Worker.organization_id == organization_id,
        ]
        if status is not None:
            conditions.append(Worker.status == status)
        if not include_deleted:
            conditions.append(Worker.deleted_at.is_(None))

        stmt = select(func.count()).select_from(Worker).where(and_(*conditions))

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def update(
        self,
        worker: WorkerEntity,
        requesting_organization_id: int,
    ) -> WorkerEntity:
        """ワーカー情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Worker).where(
            Worker.id == worker.id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_worker = result.scalar_one_or_none()

        if db_worker is None:
            # IDOR攻撃検出: 実際にワーカーが存在するか確認
            check_stmt = select(Worker).where(
                Worker.id == worker.id,
                Worker.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_worker = check_result.scalar_one_or_none()

            if actual_worker is not None:
                # ワーカーは存在するが、別組織からの更新試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant update attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_update",
                        "worker_id": worker.id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_worker.organization_id,
                    },
                )

            raise WorkerNotFoundError(worker.id)

        # 更新前の値を保存（監査ログ用）
        old_values = {
            "status": db_worker.status.value,
            "skill_level": db_worker.skill_level.value if db_worker.skill_level else None,
            "experience_months": db_worker.experience_months,
        }

        # エンティティの値でモデルを更新
        db_worker.status = worker.status
        db_worker.skill_level = worker.skill_level
        db_worker.experience_months = worker.experience_months
        db_worker.specialties = worker.specialties
        db_worker.max_tasks_per_day = worker.max_tasks_per_day
        db_worker.available_hours_per_week = worker.available_hours_per_week
        db_worker.completed_tasks_count = worker.completed_tasks_count
        db_worker.success_rate = worker.success_rate
        db_worker.average_task_time_minutes = worker.average_task_time_minutes
        db_worker.rating = worker.rating
        db_worker.notes = worker.notes

        await self._session.flush()
        await self._session.refresh(db_worker)

        # セキュリティログ: ワーカー更新成功
        logger.info(
            "Worker updated successfully",
            extra={
                "event_type": "worker_updated",
                "worker_id": worker.id,
                "organization_id": requesting_organization_id,
                "old_values": old_values,
                "new_values": {
                    "status": worker.status.value,
                    "skill_level": worker.skill_level.value if worker.skill_level else None,
                    "experience_months": worker.experience_months,
                },
            },
        )

        return self._to_entity(db_worker)

    async def soft_delete(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> None:
        """ワーカーを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Worker).where(
            Worker.id == worker_id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        worker = result.scalar_one_or_none()

        if worker is None:
            # IDOR攻撃検出: 実際にワーカーが存在するか確認
            check_stmt = select(Worker).where(
                Worker.id == worker_id,
                Worker.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_worker = check_result.scalar_one_or_none()

            if actual_worker is not None:
                # ワーカーは存在するが、別組織からの削除試行 = IDOR攻撃の可能性
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant delete attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_delete",
                        "worker_id": worker_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_worker.organization_id,
                    },
                )

            raise WorkerNotFoundError(worker_id)

        worker.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        # セキュリティログ: ワーカー削除成功
        logger.info(
            "Worker soft deleted successfully",
            extra={
                "event_type": "worker_deleted",
                "worker_id": worker_id,
                "user_id": worker.user_id,
                "organization_id": requesting_organization_id,
            },
        )

    def _to_entity(self, worker: Worker) -> WorkerEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return WorkerEntity(
            id=worker.id,
            user_id=worker.user_id,
            organization_id=worker.organization_id,
            status=worker.status,
            skill_level=worker.skill_level,
            experience_months=worker.experience_months,
            specialties=worker.specialties,
            max_tasks_per_day=worker.max_tasks_per_day,
            available_hours_per_week=worker.available_hours_per_week,
            completed_tasks_count=worker.completed_tasks_count,
            success_rate=float(worker.success_rate) if worker.success_rate is not None else None,
            average_task_time_minutes=worker.average_task_time_minutes,
            rating=float(worker.rating) if worker.rating is not None else None,
            notes=worker.notes,
            created_at=worker.created_at,
            updated_at=worker.updated_at,
            deleted_at=worker.deleted_at,
        )
