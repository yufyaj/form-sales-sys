"""
リスト項目割り当て管理APIルーター

リスト項目とワーカーの割り当て関係のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.list_item_assignment import (
    BulkAssignRequest,
    BulkAssignResponse,
    ListItemAssignmentResponse,
)
from src.application.use_cases.list_item_assignment_use_cases import (
    ListItemAssignmentUseCases,
)
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.list_item_assignment_repository import (
    ListItemAssignmentRepository,
)

router = APIRouter(tags=["list-item-assignments"])


async def get_assignment_use_cases(
    session: AsyncSession = Depends(get_db),
) -> ListItemAssignmentUseCases:
    """
    リスト項目割り当てユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        ListItemAssignmentUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    assignment_repo = ListItemAssignmentRepository(session)

    # ユースケースをインスタンス化
    use_cases = ListItemAssignmentUseCases(assignment_repository=assignment_repo)

    return use_cases


@router.post(
    "/lists/{list_id}/assign-workers",
    response_model=BulkAssignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="リストへのワーカー一括割り当て",
    description="リスト内の未割り当て項目にワーカーを一括割り当てします。認証が必要です。",
)
async def bulk_assign_workers_to_list(
    list_id: int,
    request: BulkAssignRequest,
    use_cases: ListItemAssignmentUseCases = Depends(get_assignment_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> BulkAssignResponse:
    """
    リストへのワーカー一括割り当て

    - **list_id**: リストID
    - **worker_id**: ワーカーID
    - **count**: 割り当て件数（最大1000件）

    既に割り当て済みのリスト項目は除外されます。
    未割り当て項目が指定件数より少ない場合、利用可能な全項目を割り当てます。
    """
    assignments = await use_cases.bulk_assign_workers_to_list(
        list_id=list_id,
        worker_id=request.worker_id,
        count=request.count,
        requesting_organization_id=current_user.organization_id,
    )

    return BulkAssignResponse(
        assigned_count=len(assignments),
        assignments=[ListItemAssignmentResponse.model_validate(a) for a in assignments],
    )


@router.delete(
    "/list-item-assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="割り当て解除",
    description="リスト項目からワーカーの割り当てを解除します。認証が必要です。",
)
async def unassign_worker(
    assignment_id: int,
    use_cases: ListItemAssignmentUseCases = Depends(get_assignment_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    割り当て解除

    - **assignment_id**: 割り当てID
    """
    await use_cases.unassign_worker(
        assignment_id=assignment_id,
        requesting_organization_id=current_user.organization_id,
    )
