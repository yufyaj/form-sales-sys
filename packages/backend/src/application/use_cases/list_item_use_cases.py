"""
リスト項目ユースケース

リスト項目の更新に関するビジネスロジックを実装します。
"""

from src.application.schemas.list_item import (
    ListItemStatusUpdateRequest,
    ListItemUpdateRequest,
)
from src.domain.entities.list_item_entity import ListItemEntity
from src.domain.exceptions import ListItemNotFoundError
from src.domain.interfaces.list_item_repository import IListItemRepository


class ListItemUseCases:
    """
    リスト項目ユースケース

    リスト項目の更新操作を提供します。
    """

    def __init__(self, list_item_repository: IListItemRepository) -> None:
        """
        Args:
            list_item_repository: リスト項目リポジトリ
        """
        self._list_item_repository = list_item_repository

    async def update_list_item(
        self,
        list_item_id: int,
        requesting_organization_id: int,
        request: ListItemUpdateRequest,
    ) -> ListItemEntity:
        """
        リスト項目を更新（会社名以外のフィールド）

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            ListItemEntity: 更新されたリスト項目エンティティ

        Raises:
            ListItemNotFoundError: リスト項目が見つからない場合
        """
        # リスト項目を取得（IDOR脆弱性対策）
        list_item = await self._list_item_repository.find_by_id(
            list_item_id, requesting_organization_id
        )

        if list_item is None:
            raise ListItemNotFoundError(list_item_id)

        # 変更があるかチェック
        has_changes = False

        # ステータスの更新
        if request.status is not None and request.status != list_item.status:
            list_item.status = request.status
            has_changes = True

        # 変更がない場合は既存のエンティティをそのまま返す
        if not has_changes:
            return list_item

        # リポジトリを使用して更新（IDOR脆弱性対策）
        updated_list_item = await self._list_item_repository.update(
            list_item, requesting_organization_id
        )

        return updated_list_item

    async def update_list_item_status(
        self,
        list_item_id: int,
        requesting_organization_id: int,
        request: ListItemStatusUpdateRequest,
    ) -> ListItemEntity:
        """
        リスト項目のステータスを更新

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            request: ステータス更新リクエスト

        Returns:
            ListItemEntity: 更新されたリスト項目エンティティ

        Raises:
            ListItemNotFoundError: リスト項目が見つからない場合
        """
        # リスト項目を取得（IDOR脆弱性対策）
        list_item = await self._list_item_repository.find_by_id(
            list_item_id, requesting_organization_id
        )

        if list_item is None:
            raise ListItemNotFoundError(list_item_id)

        # ステータスが変更されていない場合は既存のエンティティを返す
        if list_item.status == request.status:
            return list_item

        # ステータスを更新
        list_item.status = request.status

        # リポジトリを使用して更新（IDOR脆弱性対策）
        updated_list_item = await self._list_item_repository.update(
            list_item, requesting_organization_id
        )

        return updated_list_item
