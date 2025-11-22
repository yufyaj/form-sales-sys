"""
リストスクリプト管理APIルーター

リストスクリプトのCRUD操作のエンドポイントを提供します。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.list_script import (
    ListScriptCreate,
    ListScriptListResponse,
    ListScriptResponse,
    ListScriptUpdate,
)
from src.application.use_cases.list_script_use_cases import ListScriptUseCases
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.list_repository import IListRepository
from src.domain.interfaces.list_script_repository import IListScriptRepository
from src.infrastructure.persistence.repositories.list_repository import ListRepository
from src.infrastructure.persistence.repositories.list_script_repository import (
    ListScriptRepository,
)

router = APIRouter(prefix="/list-scripts", tags=["list-scripts"])


async def get_list_script_use_cases(
    session: AsyncSession = Depends(get_db),
) -> ListScriptUseCases:
    """
    リストスクリプトユースケースの依存性注入

    Args:
        session: データベースセッション

    Returns:
        ListScriptUseCases: リストスクリプトユースケースインスタンス
    """
    script_repo: IListScriptRepository = ListScriptRepository(session)
    list_repo: IListRepository = ListRepository(session)
    return ListScriptUseCases(
        list_script_repository=script_repo,
        list_repository=list_repo,
    )


@router.post(
    "",
    response_model=ListScriptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="スクリプト作成",
    description="リストに新しいスクリプトを作成します。認証が必要です。",
)
async def create_script(
    request: ListScriptCreate,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListScriptUseCases = Depends(get_list_script_use_cases),
) -> ListScriptResponse:
    """
    スクリプトを作成

    - **list_id**: リストID
    - **title**: スクリプトタイトル
    - **content**: スクリプト本文（営業トークの台本）
    """
    script_entity = await use_cases.create_script(
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return ListScriptResponse.model_validate(script_entity)


@router.get(
    "/{script_id}",
    response_model=ListScriptResponse,
    summary="スクリプト取得",
    description="IDでスクリプトを取得します。認証が必要です。",
)
async def get_script(
    script_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListScriptUseCases = Depends(get_list_script_use_cases),
) -> ListScriptResponse:
    """
    スクリプトを取得

    - **script_id**: スクリプトID
    """
    script_entity = await use_cases.get_script(
        script_id=script_id,
        requesting_organization_id=current_user.organization_id,
    )
    return ListScriptResponse.model_validate(script_entity)


@router.get(
    "",
    response_model=ListScriptListResponse,
    summary="スクリプト一覧取得",
    description="リストに属するスクリプトの一覧を取得します。認証が必要です。",
)
async def list_scripts(
    list_id: Annotated[int, Query(gt=0, description="リストID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListScriptUseCases = Depends(get_list_script_use_cases),
) -> ListScriptListResponse:
    """
    リストに属するスクリプトの一覧を取得

    - **list_id**: リストID
    """
    scripts = await use_cases.list_scripts_by_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
    )

    return ListScriptListResponse(
        scripts=[ListScriptResponse.model_validate(script) for script in scripts],
        total=len(scripts),
    )


@router.patch(
    "/{script_id}",
    response_model=ListScriptResponse,
    summary="スクリプト更新",
    description="スクリプトを更新します。認証が必要です。",
)
async def update_script(
    script_id: int,
    request: ListScriptUpdate,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListScriptUseCases = Depends(get_list_script_use_cases),
) -> ListScriptResponse:
    """
    スクリプトを更新

    - **script_id**: スクリプトID
    - **request**: 更新内容（部分更新可能）
    """
    script_entity = await use_cases.update_script(
        script_id=script_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return ListScriptResponse.model_validate(script_entity)


@router.delete(
    "/{script_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="スクリプト削除",
    description="スクリプトを論理削除します。認証が必要です。",
)
async def delete_script(
    script_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListScriptUseCases = Depends(get_list_script_use_cases),
) -> None:
    """
    スクリプトを論理削除

    - **script_id**: スクリプトID
    """
    await use_cases.delete_script(
        script_id=script_id,
        requesting_organization_id=current_user.organization_id,
    )
