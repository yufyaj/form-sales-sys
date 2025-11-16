"""
顧客担当者管理APIエンドポイント

顧客担当者のCRUD操作を提供します
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.app.api.dependencies import (
    get_client_contact_use_cases,
    get_current_active_user,
)
from src.application.schemas.client_contact import (
    ClientContactCreateRequest,
    ClientContactListResponse,
    ClientContactResponse,
    ClientContactUpdateRequest,
)
from src.application.use_cases.client_contact_use_cases import ClientContactUseCases
from src.domain.entities.user_entity import UserEntity

router = APIRouter(
    prefix="/client-contacts",
    tags=["client-contacts"],
)


@router.post(
    "",
    response_model=ClientContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="顧客担当者を作成",
    description="新規顧客担当者を作成します",
)
async def create_client_contact(
    request: ClientContactCreateRequest,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientContactResponse:
    """新規顧客担当者を作成"""
    contact = await use_cases.create_client_contact(
        request, current_user.organization_id
    )
    return ClientContactResponse.model_validate(contact)


@router.get(
    "/{client_contact_id}",
    response_model=ClientContactResponse,
    summary="顧客担当者を取得",
    description="指定されたIDの顧客担当者を取得します（IDOR対策済み）",
)
async def get_client_contact(
    client_contact_id: int,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientContactResponse:
    """顧客担当者を取得（IDOR対策済み）"""
    contact = await use_cases.get_client_contact(
        client_contact_id, current_user.organization_id
    )
    return ClientContactResponse.model_validate(contact)


@router.get(
    "",
    response_model=ClientContactListResponse,
    summary="顧客担当者一覧を取得",
    description="指定された顧客組織の担当者一覧を取得します（ページネーション対応）",
)
async def list_client_contacts(
    client_organization_id: Annotated[int, Query(description="顧客組織ID", ge=1)],
    skip: Annotated[int, Query(description="スキップ件数", ge=0)] = 0,
    limit: Annotated[int, Query(description="取得件数", ge=1, le=100)] = 50,
    include_deleted: Annotated[bool, Query(description="削除済みを含める")] = False,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientContactListResponse:
    """顧客組織の担当者一覧を取得（ページネーション対応）"""
    contacts, total = await use_cases.list_client_contacts_by_organization(
        client_organization_id=client_organization_id,
        requesting_organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
    )

    return ClientContactListResponse(
        client_contacts=[
            ClientContactResponse.model_validate(contact) for contact in contacts
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/organizations/{client_organization_id}/primary",
    response_model=ClientContactResponse,
    summary="主担当者を取得",
    description="指定された顧客組織の主担当者を取得します（IDOR対策済み）",
)
async def get_primary_contact(
    client_organization_id: int,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientContactResponse:
    """顧客組織の主担当者を取得（IDOR対策済み）"""
    primary_contact = await use_cases.get_primary_contact(
        client_organization_id, current_user.organization_id
    )

    # 主担当者が見つからない場合は404エラー
    if primary_contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Primary contact not found",
        )

    return ClientContactResponse.model_validate(primary_contact)


@router.patch(
    "/{client_contact_id}",
    response_model=ClientContactResponse,
    summary="顧客担当者を更新",
    description="指定されたIDの顧客担当者情報を部分更新します（IDOR対策済み）",
)
async def update_client_contact(
    client_contact_id: int,
    request: ClientContactUpdateRequest,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> ClientContactResponse:
    """顧客担当者情報を部分更新（IDOR対策済み）"""
    updated_contact = await use_cases.update_client_contact(
        client_contact_id, current_user.organization_id, request
    )
    return ClientContactResponse.model_validate(updated_contact)


@router.delete(
    "/{client_contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="顧客担当者を削除",
    description="指定されたIDの顧客担当者を論理削除します（IDOR対策済み）",
)
async def delete_client_contact(
    client_contact_id: int,
    use_cases: Annotated[ClientContactUseCases, Depends(get_client_contact_use_cases)],
    current_user: Annotated[UserEntity, Depends(get_current_active_user)],
) -> None:
    """顧客担当者を論理削除（IDOR対策済み）"""
    await use_cases.delete_client_contact(
        client_contact_id, current_user.organization_id
    )
