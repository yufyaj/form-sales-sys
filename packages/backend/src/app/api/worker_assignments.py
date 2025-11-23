"""
ワーカー割り当てAPIルーター

ワーカーに割り当てられたリスト項目の情報を提供します
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_current_worker_id, get_db
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
    "/me/assignments",
    response_model=list[ListItemAssignmentResponse],
    summary="ワーカー割り当てリスト取得",
    description="ログイン中のワーカーに割り当てられたリスト項目の一覧を取得します。認証が必要です。",
)
async def get_worker_assignments(
    worker_id: int = Depends(get_current_worker_id),
    use_cases: WorkerAssignmentUseCases = Depends(get_worker_assignment_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> list[ListItemAssignmentResponse]:
    """
    ログイン中のワーカーに割り当てられたリスト項目の一覧を取得（IDOR対策）

    IDOR脆弱性対策として、パスパラメータでworker_idを受け取らず、
    get_current_worker_idでログイン中のユーザーのworker_idのみを使用します。
    これにより、他のワーカーの割り当て情報を閲覧することを防止します。

    エンドポイントを /workers/me/assignments に変更し、ログイン中のワーカー自身の
    情報のみを返すように設計しています。
    """
    assignments = await use_cases.get_worker_assignments(
        worker_id=worker_id,
        organization_id=current_user.organization_id,
    )
    return [ListItemAssignmentResponse.model_validate(a) for a in assignments]
