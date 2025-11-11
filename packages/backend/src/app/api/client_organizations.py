"""
顧客組織管理APIエンドポイント

顧客組織のCRUD操作を提供します
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.app.api.dependencies import (
    get_client_organization_use_cases,
    get_current_active_user,
)
from src.application.schemas.client_organization import (
    ClientOrganizationCreateRequest,
    ClientOrganizationListResponse,
    ClientOrganizationResponse,
    ClientOrganizationUpdateRequest,
)
from src.application.use_cases.client_organization_use_cases import (
    ClientOrganizationUseCases,
)
from src.domain.entities.user_entity import UserEntity

router = APIRouter(
    prefix="/client-organizations",
    tags=["client-organizations"],
)


@router.post(
    "",
    response_model=ClientOrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="顧客組織を作成",
    description="新規顧客組織を作成します",
)
async def create_client_organization(
    request: ClientOrganizationCreateRequest,
    use_cases: Annotated[
        ClientOrganizationUseCases, Depends(get_client_organization_use_cases)
    ],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientOrganizationResponse:
    """新規顧客組織を作成"""
    client_org = await use_cases.create_client_organization(
        request, current_user.organization_id
    )
    return ClientOrganizationResponse.model_validate(client_org)


@router.get(
    "/{client_organization_id}",
    response_model=ClientOrganizationResponse,
    summary="顧客組織を取得",
    description="指定されたIDの顧客組織を取得します（IDOR対策済み）",
)
async def get_client_organization(
    client_organization_id: int,
    use_cases: Annotated[
        ClientOrganizationUseCases, Depends(get_client_organization_use_cases)
    ],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientOrganizationResponse:
    """顧客組織を取得（IDOR対策済み）"""
    client_org = await use_cases.get_client_organization(
        client_organization_id, current_user.organization_id
    )
    return ClientOrganizationResponse.model_validate(client_org)


@router.get(
    "",
    response_model=ClientOrganizationListResponse,
    summary="顧客組織一覧を取得",
    description="営業支援会社の顧客組織一覧を取得します（ページネーション対応）",
)
async def list_client_organizations(
    skip: Annotated[int, Query(description="スキップ件数", ge=0)] = 0,
    limit: Annotated[int, Query(description="取得件数", ge=1, le=100)] = 50,
    include_deleted: Annotated[bool, Query(description="削除済みを含める")] = False,
    use_cases: Annotated[
        ClientOrganizationUseCases, Depends(get_client_organization_use_cases)
    ],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientOrganizationListResponse:
    """顧客組織一覧を取得（ページネーション対応）"""
    client_orgs, total = await use_cases.list_client_organizations(
        requesting_organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
    )

    return ClientOrganizationListResponse(
        client_organizations=[
            ClientOrganizationResponse.model_validate(co) for co in client_orgs
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{client_organization_id}",
    response_model=ClientOrganizationResponse,
    summary="顧客組織を更新",
    description="指定されたIDの顧客組織情報を部分更新します（IDOR対策済み）",
)
async def update_client_organization(
    client_organization_id: int,
    request: ClientOrganizationUpdateRequest,
    use_cases: Annotated[
        ClientOrganizationUseCases, Depends(get_client_organization_use_cases)
    ],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientOrganizationResponse:
    """顧客組織情報を部分更新（IDOR対策済み）"""
    updated_client_org = await use_cases.update_client_organization(
        client_organization_id, current_user.organization_id, request
    )
    return ClientOrganizationResponse.model_validate(updated_client_org)


@router.delete(
    "/{client_organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="顧客組織を削除",
    description="指定されたIDの顧客組織を論理削除します（IDOR対策済み）",
)
async def delete_client_organization(
    client_organization_id: int,
    use_cases: Annotated[
        ClientOrganizationUseCases, Depends(get_client_organization_use_cases)
    ],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> None:
    """顧客組織を論理削除（IDOR対策済み）"""
    await use_cases.delete_client_organization(
        client_organization_id, current_user.organization_id
    )
