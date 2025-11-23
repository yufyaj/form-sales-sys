"""
リスト項目ユースケースの単体テスト

TDDサイクル: Red フェーズ
ユースケースの仕様に基づき、失敗するテストを先に記述します。
"""

from unittest.mock import AsyncMock

import pytest

from src.application.schemas.list_item import (
    ListItemStatusUpdateRequest,
    ListItemUpdateRequest,
)
from src.application.use_cases.list_item_use_cases import ListItemUseCases
from src.domain.entities.list_item_entity import ListItemEntity
from src.domain.exceptions import ListItemNotFoundError


@pytest.fixture
def mock_list_item_repository() -> AsyncMock:
    """リスト項目リポジトリのモック"""
    return AsyncMock()


@pytest.fixture
def list_item_use_cases(mock_list_item_repository: AsyncMock) -> ListItemUseCases:
    """リスト項目ユースケースのインスタンス"""
    return ListItemUseCases(list_item_repository=mock_list_item_repository)


@pytest.fixture
def sample_list_item_entity() -> ListItemEntity:
    """サンプルのリスト項目エンティティ"""
    return ListItemEntity(
        id=1,
        list_id=10,
        title="株式会社サンプル",
        status="pending",
        created_at=None,
        updated_at=None,
        deleted_at=None,
    )


class TestUpdateListItem:
    """update_list_item() のテスト"""

    @pytest.mark.asyncio
    async def test_update_list_item_success(
        self,
        list_item_use_cases: ListItemUseCases,
        mock_list_item_repository: AsyncMock,
        sample_list_item_entity: ListItemEntity,
    ) -> None:
        """リスト項目の更新が成功すること"""
        # Arrange
        requesting_organization_id = 100
        list_item_id = 1
        request = ListItemUpdateRequest(status="contacted")

        # モックの戻り値を設定
        mock_list_item_repository.find_by_id.return_value = sample_list_item_entity
        updated_entity = ListItemEntity(
            id=1,
            list_id=10,
            title="株式会社サンプル",
            status="contacted",
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )
        mock_list_item_repository.update.return_value = updated_entity

        # Act
        result = await list_item_use_cases.update_list_item(
            list_item_id=list_item_id,
            requesting_organization_id=requesting_organization_id,
            request=request,
        )

        # Assert
        assert result.id == 1
        assert result.status == "contacted"
        mock_list_item_repository.find_by_id.assert_called_once_with(
            list_item_id, requesting_organization_id
        )
        mock_list_item_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_list_item_not_found(
        self,
        list_item_use_cases: ListItemUseCases,
        mock_list_item_repository: AsyncMock,
    ) -> None:
        """存在しないリスト項目を更新しようとすると例外が発生すること"""
        # Arrange
        requesting_organization_id = 100
        list_item_id = 999
        request = ListItemUpdateRequest(status="contacted")

        # モックの戻り値を設定（見つからない）
        mock_list_item_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ListItemNotFoundError):
            await list_item_use_cases.update_list_item(
                list_item_id=list_item_id,
                requesting_organization_id=requesting_organization_id,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_update_list_item_no_changes(
        self,
        list_item_use_cases: ListItemUseCases,
        mock_list_item_repository: AsyncMock,
        sample_list_item_entity: ListItemEntity,
    ) -> None:
        """変更がない場合でもエンティティを返すこと"""
        # Arrange
        requesting_organization_id = 100
        list_item_id = 1
        request = ListItemUpdateRequest()  # 何も変更しない

        # モックの戻り値を設定
        mock_list_item_repository.find_by_id.return_value = sample_list_item_entity

        # Act
        result = await list_item_use_cases.update_list_item(
            list_item_id=list_item_id,
            requesting_organization_id=requesting_organization_id,
            request=request,
        )

        # Assert
        assert result.id == 1
        assert result.status == "pending"  # 変更なし
        # find_by_idは呼ばれるが、updateは呼ばれない（変更がないため）
        mock_list_item_repository.find_by_id.assert_called_once()


class TestUpdateListItemStatus:
    """update_list_item_status() のテスト"""

    @pytest.mark.asyncio
    async def test_update_status_success(
        self,
        list_item_use_cases: ListItemUseCases,
        mock_list_item_repository: AsyncMock,
        sample_list_item_entity: ListItemEntity,
    ) -> None:
        """ステータス更新が成功すること"""
        # Arrange
        requesting_organization_id = 100
        list_item_id = 1
        request = ListItemStatusUpdateRequest(status="negotiating")

        # モックの戻り値を設定
        mock_list_item_repository.find_by_id.return_value = sample_list_item_entity
        updated_entity = ListItemEntity(
            id=1,
            list_id=10,
            title="株式会社サンプル",
            status="negotiating",
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )
        mock_list_item_repository.update.return_value = updated_entity

        # Act
        result = await list_item_use_cases.update_list_item_status(
            list_item_id=list_item_id,
            requesting_organization_id=requesting_organization_id,
            request=request,
        )

        # Assert
        assert result.id == 1
        assert result.status == "negotiating"
        mock_list_item_repository.find_by_id.assert_called_once_with(
            list_item_id, requesting_organization_id
        )
        mock_list_item_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_not_found(
        self,
        list_item_use_cases: ListItemUseCases,
        mock_list_item_repository: AsyncMock,
    ) -> None:
        """存在しないリスト項目のステータス更新で例外が発生すること"""
        # Arrange
        requesting_organization_id = 100
        list_item_id = 999
        request = ListItemStatusUpdateRequest(status="negotiating")

        # モックの戻り値を設定（見つからない）
        mock_list_item_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ListItemNotFoundError):
            await list_item_use_cases.update_list_item_status(
                list_item_id=list_item_id,
                requesting_organization_id=requesting_organization_id,
                request=request,
            )
