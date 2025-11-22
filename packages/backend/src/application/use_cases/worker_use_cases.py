"""
ワーカー管理のユースケース

ワーカーのCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.worker import (
    WorkerCreateRequest,
    WorkerUpdateRequest,
)
from src.domain.entities.worker_entity import WorkerEntity
from src.domain.exceptions import (
    UserNotFoundException,
    WorkerNotFoundError,
)
from src.domain.interfaces.user_repository import IUserRepository
from src.domain.interfaces.worker_repository import IWorkerRepository
from src.infrastructure.persistence.models.worker import WorkerStatus


class WorkerUseCases:
    """ワーカー管理のユースケースクラス"""

    def __init__(
        self,
        worker_repository: IWorkerRepository,
        user_repository: IUserRepository,
    ) -> None:
        """
        Args:
            worker_repository: ワーカーリポジトリ
            user_repository: ユーザーリポジトリ
        """
        self._worker_repo = worker_repository
        self._user_repo = user_repository

    async def create_worker(
        self,
        request: WorkerCreateRequest,
        organization_id: int,
    ) -> WorkerEntity:
        """
        新規ワーカーを作成

        Args:
            request: ワーカー作成リクエスト
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            作成されたワーカーエンティティ

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
        """
        # ユーザーの存在確認（マルチテナント対応）
        user = await self._user_repo.find_by_id_with_org(
            request.user_id, organization_id
        )
        if user is None:
            raise UserNotFoundException(user_id=request.user_id)

        # リポジトリで永続化
        worker = await self._worker_repo.create(
            user_id=request.user_id,
            organization_id=organization_id,
            status=request.status,
            skill_level=request.skill_level,
            experience_months=request.experience_months,
            specialties=request.specialties,
            max_tasks_per_day=request.max_tasks_per_day,
            available_hours_per_week=request.available_hours_per_week,
            notes=request.notes,
        )
        return worker

    async def get_worker(
        self,
        worker_id: int,
        organization_id: int,
    ) -> WorkerEntity:
        """
        ワーカーを取得

        Args:
            worker_id: ワーカーID
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            ワーカーエンティティ

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合
        """
        worker = await self._worker_repo.find_by_id(worker_id, organization_id)
        if worker is None:
            raise WorkerNotFoundError(worker_id)
        return worker

    async def list_workers(
        self,
        organization_id: int,
        status: WorkerStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[WorkerEntity], int]:
        """
        組織のワーカー一覧を取得

        Args:
            organization_id: 組織ID
            status: フィルタ用のワーカーステータス（Noneの場合は全ステータス）
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (ワーカーリスト, 総件数)のタプル
        """
        worker_list = await self._worker_repo.list_by_organization(
            organization_id=organization_id,
            status=status,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        # 総件数を正確に取得（ページネーション対応）
        total = await self._worker_repo.count_by_organization(
            organization_id=organization_id,
            status=status,
            include_deleted=False,
        )
        return worker_list, total

    async def update_worker(
        self,
        worker_id: int,
        organization_id: int,
        request: WorkerUpdateRequest,
    ) -> WorkerEntity:
        """
        ワーカー情報を更新

        Args:
            worker_id: ワーカーID
            organization_id: 組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新されたワーカーエンティティ

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合
        """
        # ワーカーを取得
        worker = await self._worker_repo.find_by_id(worker_id, organization_id)
        if worker is None:
            raise WorkerNotFoundError(worker_id)

        # フィールドを更新（リクエストに含まれるフィールドのみ）
        if request.status is not None:
            worker.status = request.status

        if request.skill_level is not None:
            worker.skill_level = request.skill_level

        if request.experience_months is not None:
            worker.experience_months = request.experience_months

        if request.specialties is not None:
            worker.specialties = request.specialties

        if request.max_tasks_per_day is not None:
            worker.max_tasks_per_day = request.max_tasks_per_day

        if request.available_hours_per_week is not None:
            worker.available_hours_per_week = request.available_hours_per_week

        if request.completed_tasks_count is not None:
            worker.completed_tasks_count = request.completed_tasks_count

        if request.success_rate is not None:
            worker.success_rate = request.success_rate

        if request.average_task_time_minutes is not None:
            worker.average_task_time_minutes = request.average_task_time_minutes

        if request.rating is not None:
            worker.rating = request.rating

        if request.notes is not None:
            worker.notes = request.notes

        # リポジトリで永続化
        updated_worker = await self._worker_repo.update(worker, organization_id)
        return updated_worker

    async def delete_worker(
        self,
        worker_id: int,
        organization_id: int,
    ) -> None:
        """
        ワーカーを論理削除

        Args:
            worker_id: ワーカーID
            organization_id: 組織ID（マルチテナント対応）

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合
        """
        await self._worker_repo.soft_delete(worker_id, organization_id)
