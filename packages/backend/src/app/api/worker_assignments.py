"""
ワーカー割り当てAPIルーター

ワーカーに割り当てられたリスト項目の情報を提供します
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.list_item_assignment import ListItemAssignmentResponse
from src.application.use_cases.worker_assignment_use_cases import WorkerAssignmentUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.list_item_assignment_repository import ListItemAssignmentRepository

router = APIRouter(prefix="/workers", tags=["worker-assignments"])


async def get_worker_assignment_use_cases(
    session: AsyncSession = Depends(get_db),
) -> WorkerAssignmentUseCases:
    """
    ワーカー割り当てユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        WorkerAssignmentUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    assignment_repo = ListItemAssignmentRepository(session)

    # ユースケースをインスタンス化
    use_cases = WorkerAssignmentUseCases(
        list_item_assignment_repository=assignment_repo,
    )

    return use_cases


@router.get(
    "/{worker_id}/assignments",
    response_model=list[ListItemAssignmentResponse],
    summary="ワーカー割り当てリスト取得",
    description="指定されたワーカーに割り当てられたリスト項目の一覧を取得します。認証が必要です。",
)
async def get_worker_assignments(
    worker_id: int,
    use_cases: WorkerAssignmentUseCases = Depends(get_worker_assignment_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> list[ListItemAssignmentResponse]:
    """
    ワーカーに割り当てられたリスト項目の一覧を取得

    - **worker_id**: ワーカーID

    IDOR対策として、organization_idでアクセス権限をチェックします。
    """
    assignments = await use_cases.get_worker_assignments(
        worker_id=worker_id,
        organization_id=current_user.organization_id,
    )
    return [ListItemAssignmentResponse.model_validate(a) for a in assignments]
