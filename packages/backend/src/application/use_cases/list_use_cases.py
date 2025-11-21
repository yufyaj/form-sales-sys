"""
List management use cases

Executes CRUD operations and business logic for lists
"""

from src.application.schemas.list import (
    ListCreateRequest,
    ListUpdateRequest,
)
from src.domain.entities.list_entity import ListEntity
from src.domain.exceptions import ListNotFoundError
from src.domain.interfaces.list_repository import IListRepository


class ListUseCases:
    """List management use case class"""

    def __init__(
        self,
        list_repository: IListRepository,
    ) -> None:
        """
        Args:
            list_repository: List repository
        """
        self._list_repo = list_repository

    async def create_list(
        self,
        requesting_organization_id: int,
        request: ListCreateRequest,
    ) -> ListEntity:
        """
        Create a new list

        Args:
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: List creation request

        Returns:
            Created list entity

        Raises:
            ValueError: If organization ID does not match (no permission)
        """
        # Security: Validate organization ownership
        if request.organization_id != requesting_organization_id:
            raise ValueError("No permission for the specified organization")

        # Create list
        list_entity = await self._list_repo.create(
            organization_id=request.organization_id,
            name=request.name,
            description=request.description,
        )

        return list_entity

    async def get_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        Get a list

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)

        Returns:
            List entity

        Raises:
            ListNotFoundError: If list is not found
        """
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        return list_entity

    async def list_lists_by_organization(
        self,
        organization_id: int,
        requesting_organization_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ListEntity], int]:
        """
        Get lists belonging to an organization

        Args:
            organization_id: Organization ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            page: Page number (1-indexed)
            page_size: Page size (max 100)

        Returns:
            Tuple of (list array, total count)

        Raises:
            ValueError: If organization ID does not match (no permission)
        """
        # Security: Validate organization ownership
        if organization_id != requesting_organization_id:
            raise ValueError("No permission for the specified organization")

        # Limit page size
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size

        # Get list of lists
        lists = await self._list_repo.list_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=page_size,
            include_deleted=False,
        )

        # Return count of retrieved lists (simple implementation)
        # For more accurate total count, add count_by_organization method to repository
        total = len(lists)

        return lists, total

    async def update_list(
        self,
        list_id: int,
        requesting_organization_id: int,
        request: ListUpdateRequest,
    ) -> ListEntity:
        """
        Update list information

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)
            request: Update request

        Returns:
            Updated list entity

        Raises:
            ListNotFoundError: If list is not found
        """
        # Get list
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Update fields
        if request.name is not None:
            list_entity.name = request.name

        if request.description is not None:
            list_entity.description = request.description

        # Persist in repository
        updated_list = await self._list_repo.update(
            list_entity=list_entity,
            requesting_organization_id=requesting_organization_id,
        )

        return updated_list

    async def delete_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        Soft delete a list

        Args:
            list_id: List ID
            requesting_organization_id: Requesting organization ID (for multi-tenancy)

        Raises:
            ListNotFoundError: If list is not found
        """
        # Check list existence
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # Execute soft delete
        await self._list_repo.soft_delete(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )

    async def duplicate_list(
        self,
        list_id: int,
        requesting_organization_id: int,
        new_name: str | None = None,
    ) -> ListEntity:
        """
        リストを複製

        Args:
            list_id: 複製元のリストID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            new_name: 新しいリスト名（指定がない場合は「{元の名前}のコピー」）

        Returns:
            複製されたリストエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
        """
        # 複製元のリストを取得
        source_list = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if source_list is None:
            raise ListNotFoundError(list_id)

        # 新しい名前が指定されていない場合はデフォルト名を生成
        if new_name is None:
            new_name = f"{source_list.name}のコピー"

        # リストを複製
        duplicated_list = await self._list_repo.duplicate(
            source_list_id=list_id,
            new_name=new_name,
            requesting_organization_id=requesting_organization_id,
        )

        return duplicated_list
