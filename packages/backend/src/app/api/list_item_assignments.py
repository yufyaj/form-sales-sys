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
    description="""
    リスト内の未割り当て項目にワーカーを一括割り当てします。

    **セキュリティ要件:**
    - JWT認証が必須です
    - リクエスト元の組織に所属するリストとワーカーのみ操作可能です（IDOR対策）
    - 論理削除されたリスト項目、ワーカーは自動的に除外されます

    **処理内容:**
    - 既に割り当て済みのリスト項目は自動的に除外されます
    - 未割り当て項目が指定件数より少ない場合、利用可能な全項目を割り当てます
    - 最大1000件まで一括割り当て可能です
    - データベースの一括INSERTにより効率的に処理されます

    **エラー:**
    - 400: リストまたはワーカーが見つからない、または他組織のリソース
    - 401: 認証が必要
    - 422: バリデーションエラー（件数が0以下、1000超過など）
    """,
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
    - **worker_id**: ワーカーID（1以上の整数）
    - **count**: 割り当て件数（1〜1000の整数）

    **レスポンス:**
    - **assigned_count**: 実際に割り当てられた件数
    - **assignments**: 作成された割り当てのリスト（各割り当てにID、リスト項目ID、ワーカーID、作成日時、更新日時を含む）

    **処理の流れ:**
    1. リストとワーカーの存在確認（マルチテナント分離）
    2. 未割り当て項目の抽出（既存割り当て、論理削除を除外）
    3. 指定件数分を一括割り当て
    4. 割り当て結果を返却
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
    description="""
    リスト項目からワーカーの割り当てを解除します（物理削除）。

    **セキュリティ要件:**
    - JWT認証が必須です
    - リクエスト元の組織に所属する割り当てのみ削除可能です（IDOR対策）

    **処理内容:**
    - 割り当てレコードを物理削除します（中間テーブルのため論理削除は行いません）
    - 削除後、該当リスト項目は再度未割り当て状態になります

    **エラー:**
    - 400: 割り当てが見つからない、または他組織の割り当て
    - 401: 認証が必要
    """,
)
async def unassign_worker(
    assignment_id: int,
    use_cases: ListItemAssignmentUseCases = Depends(get_assignment_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    割り当て解除

    - **assignment_id**: 割り当てID（削除する割り当てレコードのID）

    **レスポンス:**
    - 204 No Content（成功時はボディなし）

    **処理の流れ:**
    1. 割り当ての存在確認（マルチテナント分離）
    2. 割り当てレコードを物理削除
    3. データベースにflush
    """
    await use_cases.unassign_worker(
        assignment_id=assignment_id,
        requesting_organization_id=current_user.organization_id,
    )
