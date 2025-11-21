"""
Unit tests for list use cases

Test business logic using mocks
"""
from unittest.mock import AsyncMock

import pytest

from src.application.schemas.list import (
    ListCreateRequest,
    ListUpdateRequest,
)
from src.application.use_cases.list_use_cases import ListUseCases
from src.domain.entities.list_entity import ListEntity
from src.domain.exceptions import ListNotFoundError


@pytest.fixture
def mock_list_repository() -> AsyncMock:
    """Create mock list repository"""
    return AsyncMock()


@pytest.fixture
def list_use_cases(mock_list_repository: AsyncMock) -> ListUseCases:
    """Create list use cases instance"""
    return ListUseCases(list_repository=mock_list_repository)


class TestListUseCases:
    """Test class for ListUseCases"""

    @pytest.mark.asyncio
    async def test_create_list_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List creation succeeds"""
        # Arrange
        request = ListCreateRequest(
            organization_id=10,
            name="January 2025 Campaign Target Companies",
            description="List for new customer development",
        )

        expected_entity = ListEntity(
            id=1,
            organization_id=10,
            name="January 2025 Campaign Target Companies",
            description="List for new customer development",
        )

        mock_list_repository.create.return_value = expected_entity

        # Act
        result = await list_use_cases.create_list(
            requesting_organization_id=10,
            request=request,
        )

        # Assert
        assert result == expected_entity
        mock_list_repository.create.assert_called_once()
        call_kwargs = mock_list_repository.create.call_args.kwargs
        assert call_kwargs["organization_id"] == 10
        assert call_kwargs["name"] == "January 2025 Campaign Target Companies"
        assert call_kwargs["description"] == "List for new customer development"

    @pytest.mark.asyncio
    async def test_create_list_validates_organization_ownership(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """Validate organization ownership when creating list"""
        # Arrange
        request = ListCreateRequest(
            organization_id=10,
            name="Test List",
        )

        # Act & Assert
        with pytest.raises(ValueError, match="No permission"):
            await list_use_cases.create_list(
                requesting_organization_id=999,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_get_list_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List retrieval succeeds"""
        # Arrange
        expected_entity = ListEntity(
            id=1,
            organization_id=10,
            name="Test List",
        )

        mock_list_repository.find_by_id.return_value = expected_entity

        # Act
        result = await list_use_cases.get_list(
            list_id=1,
            requesting_organization_id=10,
        )

        # Assert
        assert result == expected_entity
        mock_list_repository.find_by_id.assert_called_once_with(
            list_id=1,
            requesting_organization_id=10,
        )

    @pytest.mark.asyncio
    async def test_get_list_raises_not_found_error(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """get_list raises exception when list is not found"""
        # Arrange
        mock_list_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await list_use_cases.get_list(
                list_id=1,
                requesting_organization_id=10,
            )

    @pytest.mark.asyncio
    async def test_list_lists_by_organization_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List retrieval by organization succeeds"""
        # Arrange
        expected_entities = [
            ListEntity(
                id=1,
                organization_id=10,
                name="List 1",
            ),
            ListEntity(
                id=2,
                organization_id=10,
                name="List 2",
            ),
        ]

        mock_list_repository.list_by_organization.return_value = expected_entities

        # Act
        lists, total = await list_use_cases.list_lists_by_organization(
            organization_id=10,
            requesting_organization_id=10,
            page=1,
            page_size=20,
        )

        # Assert
        assert lists == expected_entities
        assert total == 2
        mock_list_repository.list_by_organization.assert_called_once_with(
            organization_id=10,
            skip=0,
            limit=20,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_lists_by_organization_with_pagination(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List retrieval by organization succeeds with pagination"""
        # Arrange
        mock_list_repository.list_by_organization.return_value = []

        # Act
        await list_use_cases.list_lists_by_organization(
            organization_id=10,
            requesting_organization_id=10,
            page=3,
            page_size=50,
        )

        # Assert
        mock_list_repository.list_by_organization.assert_called_once_with(
            organization_id=10,
            skip=100,
            limit=50,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_lists_by_organization_limits_page_size_to_100(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """Page size is limited to 100 when it exceeds 100"""
        # Arrange
        mock_list_repository.list_by_organization.return_value = []

        # Act
        await list_use_cases.list_lists_by_organization(
            organization_id=10,
            requesting_organization_id=10,
            page=1,
            page_size=200,
        )

        # Assert
        call_kwargs = mock_list_repository.list_by_organization.call_args.kwargs
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_list_lists_by_organization_validates_ownership(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """Validate organization ownership when listing"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="No permission"):
            await list_use_cases.list_lists_by_organization(
                organization_id=10,
                requesting_organization_id=999,
                page=1,
                page_size=20,
            )

    @pytest.mark.asyncio
    async def test_update_list_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List update succeeds"""
        # Arrange
        existing_list = ListEntity(
            id=1,
            organization_id=10,
            name="Old List Name",
        )

        updated_list = ListEntity(
            id=1,
            organization_id=10,
            name="New List Name",
            description="Updated description",
        )

        mock_list_repository.find_by_id.return_value = existing_list
        mock_list_repository.update.return_value = updated_list

        request = ListUpdateRequest(
            name="New List Name",
            description="Updated description",
        )

        # Act
        result = await list_use_cases.update_list(
            list_id=1,
            requesting_organization_id=10,
            request=request,
        )

        # Assert
        assert result == updated_list
        mock_list_repository.find_by_id.assert_called_once_with(
            list_id=1,
            requesting_organization_id=10,
        )
        mock_list_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_list_raises_not_found_error(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """update_list raises exception when list is not found"""
        # Arrange
        mock_list_repository.find_by_id.return_value = None

        request = ListUpdateRequest(name="New List Name")

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await list_use_cases.update_list(
                list_id=1,
                requesting_organization_id=10,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_update_list_updates_only_specified_fields(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """Only specified fields are updated"""
        # Arrange
        existing_list = ListEntity(
            id=1,
            organization_id=10,
            name="Old List Name",
            description="Old description",
        )

        mock_list_repository.find_by_id.return_value = existing_list
        mock_list_repository.update.return_value = existing_list

        request = ListUpdateRequest(name="New List Name")

        # Act
        await list_use_cases.update_list(
            list_id=1,
            requesting_organization_id=10,
            request=request,
        )

        # Assert
        update_call_args = mock_list_repository.update.call_args.kwargs
        updated_entity = update_call_args["list_entity"]
        assert updated_entity.name == "New List Name"
        assert updated_entity.description == "Old description"

    @pytest.mark.asyncio
    async def test_delete_list_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """List deletion succeeds"""
        # Arrange
        existing_list = ListEntity(
            id=1,
            organization_id=10,
            name="Test List",
        )

        mock_list_repository.find_by_id.return_value = existing_list

        # Act
        await list_use_cases.delete_list(
            list_id=1,
            requesting_organization_id=10,
        )

        # Assert
        mock_list_repository.find_by_id.assert_called_once_with(
            list_id=1,
            requesting_organization_id=10,
        )
        mock_list_repository.soft_delete.assert_called_once_with(
            list_id=1,
            requesting_organization_id=10,
        )

    @pytest.mark.asyncio
    async def test_delete_list_raises_not_found_error(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """delete_list raises exception when list is not found"""
        # Arrange
        mock_list_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await list_use_cases.delete_list(
                list_id=1,
                requesting_organization_id=10,
            )

    @pytest.mark.asyncio
    async def test_duplicate_list_success(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """リスト複製が成功する"""
        # Arrange
        source_list = ListEntity(
            id=1,
            organization_id=10,
            name="元のリスト",
            description="元の説明",
        )

        duplicated_list = ListEntity(
            id=2,
            organization_id=10,
            name="元のリストのコピー",
            description="元の説明",
        )

        mock_list_repository.find_by_id.return_value = source_list
        mock_list_repository.duplicate.return_value = duplicated_list

        # Act
        result = await list_use_cases.duplicate_list(
            list_id=1,
            requesting_organization_id=10,
            new_name="元のリストのコピー",
        )

        # Assert
        assert result == duplicated_list
        mock_list_repository.find_by_id.assert_called_once_with(
            list_id=1,
            requesting_organization_id=10,
        )
        mock_list_repository.duplicate.assert_called_once_with(
            source_list_id=1,
            new_name="元のリストのコピー",
            requesting_organization_id=10,
        )

    @pytest.mark.asyncio
    async def test_duplicate_list_raises_not_found_error(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """複製元のリストが存在しない場合に例外を発生させる"""
        # Arrange
        mock_list_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await list_use_cases.duplicate_list(
                list_id=1,
                requesting_organization_id=10,
                new_name="コピー",
            )

    @pytest.mark.asyncio
    async def test_duplicate_list_generates_default_name_if_not_provided(
        self,
        list_use_cases: ListUseCases,
        mock_list_repository: AsyncMock,
    ) -> None:
        """新しいリスト名が指定されない場合、タイムスタンプ付きのデフォルト名が生成される"""
        # Arrange
        source_list = ListEntity(
            id=1,
            organization_id=10,
            name="元のリスト",
            description="元の説明",
        )

        duplicated_list = ListEntity(
            id=2,
            organization_id=10,
            name="元のリストのコピー_20251121_192500",
            description="元の説明",
        )

        mock_list_repository.find_by_id.return_value = source_list
        mock_list_repository.duplicate.return_value = duplicated_list

        # Act
        result = await list_use_cases.duplicate_list(
            list_id=1,
            requesting_organization_id=10,
            new_name=None,
        )

        # Assert
        assert result == duplicated_list
        # デフォルト名にタイムスタンプが含まれることを確認
        call_kwargs = mock_list_repository.duplicate.call_args.kwargs
        generated_name = call_kwargs["new_name"]
        assert generated_name.startswith("元のリストのコピー_")
        # タイムスタンプ形式（YYYYMMDD_HHMMSS）を確認
        import re

        assert re.match(r"元のリストのコピー_\d{8}_\d{6}", generated_name)
