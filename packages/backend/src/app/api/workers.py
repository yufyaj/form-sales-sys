"""
ワーカー管理APIルーター

ワーカーのCRUD操作のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.worker import (
    WorkerCreateRequest,
    WorkerListResponse,
    WorkerResponse,
    WorkerUpdateRequest,
)
from src.application.use_cases.worker_use_cases import WorkerUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.models.worker import WorkerStatus
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.worker_repository import WorkerRepository

router = APIRouter(prefix="/workers", tags=["workers"])


async def get_worker_use_cases(
    session: AsyncSession = Depends(get_db),
) -> WorkerUseCases:
    """
    ワーカーユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        WorkerUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    worker_repo = WorkerRepository(session)
    user_repo = UserRepository(session)

    # ユースケースをインスタンス化
    use_cases = WorkerUseCases(
        worker_repository=worker_repo,
        user_repository=user_repo,
    )

    return use_cases


@router.post(
    "",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ワーカー作成",
    description="新規ワーカーを作成します。認証が必要です。",
)
async def create_worker(
    request: WorkerCreateRequest,
    use_cases: WorkerUseCases = Depends(get_worker_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerResponse:
    """
    新規ワーカーを作成

    - **user_id**: ユーザーID（対応するUserレコードのID）
    - **status**: ワーカーステータス（オプション、デフォルト: pending）
    - **skill_level**: スキルレベル（オプション）
    - **experience_months**: 経験月数（オプション）
    - **specialties**: 得意分野・専門領域（オプション）
    - **max_tasks_per_day**: 1日の最大タスク数（オプション）
    - **available_hours_per_week**: 週間稼働可能時間（オプション）
    - **notes**: 管理者用メモ・備考（オプション）
    """
    worker = await use_cases.create_worker(request, current_user.organization_id)
    return WorkerResponse.model_validate(worker)


@router.get(
    "/{worker_id}",
    response_model=WorkerResponse,
    summary="ワーカー取得",
    description="指定されたIDのワーカーを取得します。認証が必要です。",
)
async def get_worker(
    worker_id: int,
    use_cases: WorkerUseCases = Depends(get_worker_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerResponse:
    """
    ワーカーを取得

    - **worker_id**: ワーカーID
    """
    worker = await use_cases.get_worker(worker_id, current_user.organization_id)
    return WorkerResponse.model_validate(worker)


@router.get(
    "",
    response_model=WorkerListResponse,
    summary="ワーカー一覧取得",
    description="組織に所属するワーカー一覧を取得します。認証が必要です。",
)
async def list_workers(
    status: WorkerStatus | None = Query(None, description="フィルタ用ワーカーステータス"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=500, description="取得する最大件数"),
    use_cases: WorkerUseCases = Depends(get_worker_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerListResponse:
    """
    組織のワーカー一覧を取得

    - **status**: フィルタ用ワーカーステータス（オプション）
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    worker_list, total = await use_cases.list_workers(
        current_user.organization_id, status, skip, limit
    )
    return WorkerListResponse(
        workers=[WorkerResponse.model_validate(w) for w in worker_list],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{worker_id}",
    response_model=WorkerResponse,
    summary="ワーカー更新",
    description="ワーカー情報を更新します。認証が必要です。",
)
async def update_worker(
    worker_id: int,
    request: WorkerUpdateRequest,
    use_cases: WorkerUseCases = Depends(get_worker_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerResponse:
    """
    ワーカー情報を更新

    - **worker_id**: ワーカーID
    - **request**: 更新内容（部分更新可能）
    """
    worker = await use_cases.update_worker(
        worker_id, current_user.organization_id, request
    )
    return WorkerResponse.model_validate(worker)


@router.delete(
    "/{worker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ワーカー削除",
    description="ワーカーを論理削除します。認証が必要です。",
)
async def delete_worker(
    worker_id: int,
    use_cases: WorkerUseCases = Depends(get_worker_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    ワーカーを論理削除

    - **worker_id**: ワーカーID
    """
    await use_cases.delete_worker(worker_id, current_user.organization_id)
