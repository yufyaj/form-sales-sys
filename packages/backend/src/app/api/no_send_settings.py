"""
NoSendSetting management API router

Provides endpoints for no-send setting CRUD operations
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.no_send_setting import (
    NoSendSettingDayOfWeekCreate,
    NoSendSettingTimeRangeCreate,
    NoSendSettingSpecificDateCreate,
    NoSendSettingUpdateRequest,
    NoSendSettingResponse,
    NoSendSettingListResponse,
)
from src.application.use_cases.no_send_setting_use_cases import NoSendSettingUseCases
from src.domain.entities.no_send_setting_entity import NoSendSettingEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.no_send_setting_repository import INoSendSettingRepository
from src.domain.interfaces.list_repository import IListRepository
from src.infrastructure.persistence.repositories.no_send_setting_repository import (
    NoSendSettingRepository,
)
from src.infrastructure.persistence.repositories.list_repository import ListRepository

router = APIRouter(prefix="/no-send-settings", tags=["no-send-settings"])


async def get_no_send_setting_use_cases(
    session: AsyncSession = Depends(get_db),
) -> NoSendSettingUseCases:
    """
    NoSendSetting use cases dependency injection

    Args:
        session: Database session

    Returns:
        NoSendSettingUseCases: NoSendSetting use cases instance
    """
    no_send_setting_repo: INoSendSettingRepository = NoSendSettingRepository(session)
    list_repo: IListRepository = ListRepository(session)
    return NoSendSettingUseCases(
        no_send_setting_repository=no_send_setting_repo,
        list_repository=list_repo,
    )


@router.post(
    "/day-of-week",
    response_model=NoSendSettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create day-of-week no-send setting",
    description="Create a day-of-week based no-send setting. Authentication required.",
)
async def create_day_of_week_setting(
    request: NoSendSettingDayOfWeekCreate,
    list_id: Annotated[int, Query(gt=0, description="List ID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> NoSendSettingResponse:
    """
    Create a day-of-week based no-send setting

    - **list_id**: List ID
    - **name**: Setting name
    - **description**: Setting description (optional)
    - **is_enabled**: Enable/disable flag (default: true)
    - **day_of_week_list**: List of days to prohibit sending [1=Mon, 7=Sun]
    """
    setting_entity = await use_cases.create_day_of_week_setting(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(setting_entity)


@router.post(
    "/time-range",
    response_model=NoSendSettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create time-range no-send setting",
    description="Create a time-range based no-send setting. Authentication required.",
)
async def create_time_range_setting(
    request: NoSendSettingTimeRangeCreate,
    list_id: Annotated[int, Query(gt=0, description="List ID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> NoSendSettingResponse:
    """
    Create a time-range based no-send setting

    - **list_id**: List ID
    - **name**: Setting name
    - **description**: Setting description (optional)
    - **is_enabled**: Enable/disable flag (default: true)
    - **time_start**: Start time to prohibit sending (e.g., 22:00:00)
    - **time_end**: End time to prohibit sending (e.g., 08:00:00)
    """
    setting_entity = await use_cases.create_time_range_setting(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(setting_entity)


@router.post(
    "/specific-date",
    response_model=NoSendSettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create specific-date no-send setting",
    description="Create a specific-date based no-send setting. Authentication required.",
)
async def create_specific_date_setting(
    request: NoSendSettingSpecificDateCreate,
    list_id: Annotated[int, Query(gt=0, description="List ID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> NoSendSettingResponse:
    """
    Create a specific-date based no-send setting

    - **list_id**: List ID
    - **name**: Setting name
    - **description**: Setting description (optional)
    - **is_enabled**: Enable/disable flag (default: true)
    - **specific_date**: Single date to prohibit sending (e.g., 2025-01-01)
    - **date_range_start/end**: Date range to prohibit sending (alternative to specific_date)
    """
    setting_entity = await use_cases.create_specific_date_setting(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(setting_entity)


@router.get(
    "/{setting_id}",
    response_model=NoSendSettingResponse,
    summary="Get no-send setting",
    description="Get a no-send setting by ID. Authentication required.",
)
async def get_no_send_setting(
    setting_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> NoSendSettingResponse:
    """
    Get a no-send setting

    - **setting_id**: NoSendSetting ID
    """
    setting_entity = await use_cases.get_no_send_setting(
        no_send_setting_id=setting_id,
        requesting_organization_id=current_user.organization_id,
    )
    return _to_response(setting_entity)


@router.get(
    "",
    response_model=NoSendSettingListResponse,
    summary="Get no-send settings by list",
    description="Get no-send settings belonging to a list.",
)
async def list_no_send_settings(
    list_id: Annotated[int, Query(gt=0, description="List ID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
    include_disabled: Annotated[
        bool, Query(description="Include disabled settings")
    ] = False,
) -> NoSendSettingListResponse:
    """
    Get no-send settings belonging to a list

    - **list_id**: List ID
    - **include_disabled**: Include disabled settings (default: false)
    """
    settings, total = await use_cases.list_no_send_settings_by_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
        include_disabled=include_disabled,
    )

    return NoSendSettingListResponse(
        settings=[_to_response(setting_entity) for setting_entity in settings],
        total=total,
    )


@router.patch(
    "/{setting_id}",
    response_model=NoSendSettingResponse,
    summary="Update no-send setting",
    description="Update no-send setting information.",
)
async def update_no_send_setting(
    setting_id: int,
    request: NoSendSettingUpdateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> NoSendSettingResponse:
    """
    Update no-send setting information

    - **setting_id**: NoSendSetting ID
    - **name**: Setting name (optional)
    - **description**: Setting description (optional)
    - **is_enabled**: Enable/disable flag (optional)
    """
    setting_entity = await use_cases.update_no_send_setting(
        no_send_setting_id=setting_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(setting_entity)


@router.delete(
    "/{setting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete no-send setting",
    description="Soft delete a no-send setting.",
)
async def delete_no_send_setting(
    setting_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NoSendSettingUseCases = Depends(get_no_send_setting_use_cases),
) -> None:
    """
    Soft delete a no-send setting

    - **setting_id**: NoSendSetting ID
    """
    await use_cases.delete_no_send_setting(
        no_send_setting_id=setting_id,
        requesting_organization_id=current_user.organization_id,
    )


def _to_response(setting_entity: NoSendSettingEntity) -> NoSendSettingResponse:
    """
    Convert NoSendSettingEntity to NoSendSettingResponse

    Args:
        setting_entity: NoSendSetting entity

    Returns:
        NoSendSettingResponse: NoSendSetting response
    """
    return NoSendSettingResponse(
        id=setting_entity.id,
        list_id=setting_entity.list_id,
        setting_type=setting_entity.setting_type,
        name=setting_entity.name,
        description=setting_entity.description,
        is_enabled=setting_entity.is_enabled,
        day_of_week_list=setting_entity.day_of_week_list,
        time_start=setting_entity.time_start,
        time_end=setting_entity.time_end,
        specific_date=setting_entity.specific_date,
        date_range_start=setting_entity.date_range_start,
        date_range_end=setting_entity.date_range_end,
        created_at=setting_entity.created_at,
        updated_at=setting_entity.updated_at,
        deleted_at=setting_entity.deleted_at,
    )
