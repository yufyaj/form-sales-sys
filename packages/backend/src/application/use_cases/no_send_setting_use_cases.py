"""
NoSendSetting management use cases

Executes CRUD operations and business logic for no-send settings
"""

from src.application.schemas.no_send_setting import (
    NoSendSettingDayOfWeekCreate,
    NoSendSettingTimeRangeCreate,
    NoSendSettingSpecificDateCreate,
    NoSendSettingUpdateRequest,
)
from src.domain.entities.no_send_setting_entity import NoSendSettingEntity, NoSendSettingType
from src.domain.exceptions import NoSendSettingNotFoundError, ListNotFoundError
from src.domain.interfaces.no_send_setting_repository import INoSendSettingRepository
from src.domain.interfaces.list_repository import IListRepository


class NoSendSettingUseCases:
    """NoSendSetting management use case class"""

    def __init__(
        self,
        no_send_setting_repository: INoSendSettingRepository,
        list_repository: IListRepository,
    ) -> None:
        """
        Args:
            no_send_setting_repository: NoSendSetting repository
            list_repository: List repository
        """
        self._no_send_setting_repo = no_send_setting_repository
        self._list_repo = list_repository

    async def create_day_of_week_setting(
        self,
        list_id: int,
        requesting_organization_id: int,
        request: NoSendSettingDayOfWeekCreate,
    ) -> NoSendSettingEntity:
        """
        Create a day-of-week based no-send setting

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: Day of week setting creation request

        Returns:
            Created no-send setting entity

        Raises:
            ListNotFoundError: If list is not found
        """
        # Security: リストの所有権を確認
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Create setting
        setting_entity = await self._no_send_setting_repo.create(
            list_id=list_id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name=request.name,
            description=request.description,
            is_enabled=request.is_enabled,
            day_of_week_list=[day.value for day in request.day_of_week_list],
        )

        return setting_entity

    async def create_time_range_setting(
        self,
        list_id: int,
        requesting_organization_id: int,
        request: NoSendSettingTimeRangeCreate,
    ) -> NoSendSettingEntity:
        """
        Create a time-range based no-send setting

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: Time range setting creation request

        Returns:
            Created no-send setting entity

        Raises:
            ListNotFoundError: If list is not found
        """
        # Security: リストの所有権を確認
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Create setting
        setting_entity = await self._no_send_setting_repo.create(
            list_id=list_id,
            setting_type=NoSendSettingType.TIME_RANGE,
            name=request.name,
            description=request.description,
            is_enabled=request.is_enabled,
            time_start=request.time_start,
            time_end=request.time_end,
        )

        return setting_entity

    async def create_specific_date_setting(
        self,
        list_id: int,
        requesting_organization_id: int,
        request: NoSendSettingSpecificDateCreate,
    ) -> NoSendSettingEntity:
        """
        Create a specific-date based no-send setting

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: Specific date setting creation request

        Returns:
            Created no-send setting entity

        Raises:
            ListNotFoundError: If list is not found
        """
        # Security: リストの所有権を確認
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Create setting
        setting_entity = await self._no_send_setting_repo.create(
            list_id=list_id,
            setting_type=NoSendSettingType.SPECIFIC_DATE,
            name=request.name,
            description=request.description,
            is_enabled=request.is_enabled,
            specific_date=request.specific_date,
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end,
        )

        return setting_entity

    async def get_no_send_setting(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> NoSendSettingEntity:
        """
        Get a no-send setting

        Args:
            no_send_setting_id: NoSendSetting ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)

        Returns:
            NoSendSetting entity

        Raises:
            NoSendSettingNotFoundError: If no-send setting is not found
        """
        setting_entity = await self._no_send_setting_repo.find_by_id(
            no_send_setting_id=no_send_setting_id,
            requesting_organization_id=requesting_organization_id,
        )
        if setting_entity is None:
            raise NoSendSettingNotFoundError(no_send_setting_id)

        return setting_entity

    async def list_no_send_settings_by_list(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_disabled: bool = False,
    ) -> tuple[list[NoSendSettingEntity], int]:
        """
        Get no-send settings belonging to a list

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            include_disabled: Include disabled settings

        Returns:
            Tuple of (settings array, total count)

        Raises:
            ListNotFoundError: If list is not found
        """
        # Security: リストの所有権を確認
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Get list of settings
        settings = await self._no_send_setting_repo.list_by_list_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
            include_disabled=include_disabled,
            include_deleted=False,
        )

        # Return count of retrieved settings
        total = len(settings)

        return settings, total

    async def update_no_send_setting(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
        request: NoSendSettingUpdateRequest,
    ) -> NoSendSettingEntity:
        """
        Update no-send setting information

        Args:
            no_send_setting_id: NoSendSetting ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: Update request

        Returns:
            Updated no-send setting entity

        Raises:
            NoSendSettingNotFoundError: If no-send setting is not found
        """
        # Get setting
        setting_entity = await self._no_send_setting_repo.find_by_id(
            no_send_setting_id=no_send_setting_id,
            requesting_organization_id=requesting_organization_id,
        )
        if setting_entity is None:
            raise NoSendSettingNotFoundError(no_send_setting_id)

        # Update fields
        if request.name is not None:
            setting_entity.name = request.name

        if request.description is not None:
            setting_entity.description = request.description

        if request.is_enabled is not None:
            setting_entity.is_enabled = request.is_enabled

        # Persist in repository
        updated_setting = await self._no_send_setting_repo.update(
            no_send_setting_entity=setting_entity,
            requesting_organization_id=requesting_organization_id,
        )

        return updated_setting

    async def delete_no_send_setting(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        Soft delete a no-send setting

        Args:
            no_send_setting_id: NoSendSetting ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)

        Raises:
            NoSendSettingNotFoundError: If no-send setting is not found
        """
        # Check setting existence
        setting_entity = await self._no_send_setting_repo.find_by_id(
            no_send_setting_id=no_send_setting_id,
            requesting_organization_id=requesting_organization_id,
        )
        if setting_entity is None:
            raise NoSendSettingNotFoundError(no_send_setting_id)

        # Execute soft delete
        await self._no_send_setting_repo.soft_delete(
            no_send_setting_id=no_send_setting_id,
            requesting_organization_id=requesting_organization_id,
        )
