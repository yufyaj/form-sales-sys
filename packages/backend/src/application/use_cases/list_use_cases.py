"""
List management use cases

Executes CRUD operations and business logic for lists
"""
import logging

from src.application.schemas.list import (
    ListCreateRequest,
    ListUpdateRequest,
)
from src.application.services.authorization_service import AuthorizationService

logger = logging.getLogger(__name__)
from src.domain.entities.list_entity import ListEntity, ListStatus
from src.domain.exceptions import (
    ListCannotBeEditedError,
    ListInvalidStatusTransitionError,
    ListNotFoundError,
)
from src.domain.interfaces.list_repository import IListRepository


class ListUseCases:
    """List management use case class"""

    def __init__(
        self,
        list_repository: IListRepository,
        authorization_service: AuthorizationService | None = None,
    ) -> None:
        """
        Args:
            list_repository: List repository
            authorization_service: Authorization service (optional, will create if not provided)
        """
        self._list_repo = list_repository
        self._auth_service = authorization_service or AuthorizationService()

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
        self._auth_service.check_organization_access(
            resource_organization_id=request.organization_id,
            requesting_organization_id=requesting_organization_id,
        )

        # Create list
        list_entity = await self._list_repo.create(
            organization_id=request.organization_id,
            name=request.name,
            description=request.description,
        )

        logger.info(
            "List created",
            extra={
                "list_id": list_entity.id,
                "organization_id": requesting_organization_id,
                "action": "create_list",
            },
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
        self._auth_service.check_organization_access(
            resource_organization_id=organization_id,
            requesting_organization_id=requesting_organization_id,
        )

        # Limit page size
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size

        # Get total count (for pagination)
        total = await self._list_repo.count_by_organization(
            organization_id=organization_id,
            include_deleted=False,
        )

        # Get list of lists
        lists = await self._list_repo.list_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=page_size,
            include_deleted=False,
        )

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

        # 編集可能かチェック（検収済みの場合は編集不可）
        if not list_entity.is_editable():
            raise ListCannotBeEditedError(
                list_id=list_id,
                reason=f"List status is {list_entity.status.value}",
            )

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

        logger.info(
            "List deleted",
            extra={
                "list_id": list_id,
                "organization_id": requesting_organization_id,
                "action": "delete_list",
            },
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
            new_name: 新しいリスト名（指定がない場合は「{元の名前}のコピー_{timestamp}」）

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
        # マイクロ秒まで含めたタイムスタンプを付与して重複を防ぐ
        if new_name is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            new_name = f"{source_list.name}のコピー_{timestamp}"

        # リストを複製
        duplicated_list = await self._list_repo.duplicate(
            source_list_id=list_id,
            new_name=new_name,
            requesting_organization_id=requesting_organization_id,
        )

        return duplicated_list

    async def submit_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        リストを提出（draft/rejected -> submitted）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の組織ID

        Returns:
            提出されたリストエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
            ListInvalidStatusTransitionError: 提出できないステータスの場合
        """
        # リストを取得
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # 提出可能かチェック
        if not list_entity.can_submit():
            raise ListInvalidStatusTransitionError(
                list_id=list_id,
                current_status=list_entity.status.value,
                target_status=ListStatus.SUBMITTED.value,
            )

        # ステータスを更新
        updated_list = await self._list_repo.update_status(
            list_id=list_id,
            status=ListStatus.SUBMITTED,
            requesting_organization_id=requesting_organization_id,
        )

        logger.info(
            "List submitted",
            extra={
                "list_id": list_id,
                "organization_id": requesting_organization_id,
                "previous_status": list_entity.status.value,
                "new_status": ListStatus.SUBMITTED.value,
                "action": "submit_list",
            },
        )

        return updated_list

    async def accept_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        リストを検収（submitted -> accepted）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の組織ID

        Returns:
            検収されたリストエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
            ListInvalidStatusTransitionError: 検収できないステータスの場合
        """
        # リストを取得
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # 検収可能かチェック
        if not list_entity.can_accept():
            raise ListInvalidStatusTransitionError(
                list_id=list_id,
                current_status=list_entity.status.value,
                target_status=ListStatus.ACCEPTED.value,
            )

        # ステータスを更新
        updated_list = await self._list_repo.update_status(
            list_id=list_id,
            status=ListStatus.ACCEPTED,
            requesting_organization_id=requesting_organization_id,
        )

        logger.info(
            "List accepted",
            extra={
                "list_id": list_id,
                "organization_id": requesting_organization_id,
                "previous_status": list_entity.status.value,
                "new_status": ListStatus.ACCEPTED.value,
                "action": "accept_list",
            },
        )

        return updated_list

    async def reject_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        リストを差し戻し（submitted -> rejected）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の組織ID

        Returns:
            差し戻されたリストエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
            ListInvalidStatusTransitionError: 差し戻しできないステータスの場合
        """
        # リストを取得
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # 差し戻し可能かチェック
        if not list_entity.can_reject():
            raise ListInvalidStatusTransitionError(
                list_id=list_id,
                current_status=list_entity.status.value,
                target_status=ListStatus.REJECTED.value,
            )

        # ステータスを更新
        updated_list = await self._list_repo.update_status(
            list_id=list_id,
            status=ListStatus.REJECTED,
            requesting_organization_id=requesting_organization_id,
        )

        logger.info(
            "List rejected",
            extra={
                "list_id": list_id,
                "organization_id": requesting_organization_id,
                "previous_status": list_entity.status.value,
                "new_status": ListStatus.REJECTED.value,
                "action": "reject_list",
            },
        )

        return updated_list
