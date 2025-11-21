"""
List management API router

Provides endpoints for list CRUD operations
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.list import (
    ListCreateRequest,
    ListDuplicateRequest,
    ListListResponse,
    ListResponse,
    ListUpdateRequest,
)
from src.application.use_cases.list_use_cases import ListUseCases
from src.domain.entities.list_entity import ListEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.list_repository import IListRepository
from src.infrastructure.persistence.repositories.list_repository import ListRepository

router = APIRouter(prefix="/lists", tags=["lists"])


async def get_list_use_cases(
    session: AsyncSession = Depends(get_db),
) -> ListUseCases:
    """
    List use cases dependency injection

    Args:
        session: Database session

    Returns:
        ListUseCases: List use cases instance
    """
    list_repo: IListRepository = ListRepository(session)
    return ListUseCases(list_repository=list_repo)


@router.post(
    "",
    response_model=ListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create list",
    description="Create a new list. Authentication required.",
)
async def create_list(
    request: ListCreateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
) -> ListResponse:
    """
    Create a new list

    - **organization_id**: Organization ID of sales support company
    - **name**: List name (max 255 characters)
    - **description**: List description (optional)
    """
    list_entity = await use_cases.create_list(
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(list_entity)


@router.get(
    "/{list_id}",
    response_model=ListResponse,
    summary="Get list",
    description="Get a list by ID. Authentication required.",
)
async def get_list(
    list_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
) -> ListResponse:
    """
    Get a list

    - **list_id**: List ID
    """
    list_entity = await use_cases.get_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
    )
    return _to_response(list_entity)


@router.get(
    "",
    response_model=ListListResponse,
    summary="Get lists by organization",
    description="Get lists belonging to an organization.",
)
async def list_lists(
    organization_id: Annotated[int, Query(gt=0, description="Organization ID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Page size (max 100)")
    ] = 20,
) -> ListListResponse:
    """
    Get lists belonging to an organization

    - **organization_id**: Organization ID
    - **page**: Page number (default: 1)
    - **page_size**: Page size (default: 20, max: 100)
    """
    lists, total = await use_cases.list_lists_by_organization(
        organization_id=organization_id,
        requesting_organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
    )

    return ListListResponse(
        lists=[_to_response(list_entity) for list_entity in lists],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{list_id}",
    response_model=ListResponse,
    summary="Update list",
    description="Update list information.",
)
async def update_list(
    list_id: int,
    request: ListUpdateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
) -> ListResponse:
    """
    Update list information

    - **list_id**: List ID
    - **name**: List name (optional)
    - **description**: List description (optional)
    """
    list_entity = await use_cases.update_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(list_entity)


@router.delete(
    "/{list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete list",
    description="Soft delete a list.",
)
async def delete_list(
    list_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
) -> None:
    """
    Soft delete a list

    - **list_id**: List ID
    """
    await use_cases.delete_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
    )


@router.post(
    "/{list_id}/duplicate",
    response_model=ListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate list",
    description="Duplicate a list with all its items and custom values.",
)
async def duplicate_list(
    list_id: int,
    request: ListDuplicateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ListUseCases = Depends(get_list_use_cases),
) -> ListResponse:
    """
    リストを複製

    - **list_id**: 複製元のリストID
    - **new_name**: 新しいリスト名（省略可能、省略時は「{元の名前}のコピー」）
    """
    list_entity = await use_cases.duplicate_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        new_name=request.new_name,
    )
    return _to_response(list_entity)


def _to_response(list_entity: ListEntity) -> ListResponse:
    """
    Convert ListEntity to ListResponse

    Args:
        list_entity: List entity

    Returns:
        ListResponse: List response
    """
    return ListResponse(
        id=list_entity.id,
        organization_id=list_entity.organization_id,
        name=list_entity.name,
        description=list_entity.description,
        created_at=list_entity.created_at,
        updated_at=list_entity.updated_at,
        deleted_at=list_entity.deleted_at,
    )
