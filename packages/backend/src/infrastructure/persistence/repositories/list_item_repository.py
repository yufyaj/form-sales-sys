"""
リスト項目リポジトリの実装

IListItemRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.list_item_entity import ListItemEntity
from src.domain.exceptions import ListItemNotFoundError
from src.domain.interfaces.list_item_repository import IListItemRepository
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.list_item import ListItem


class ListItemRepository(IListItemRepository):
    """
    リスト項目リポジトリの実装

    SQLAlchemyを使用してリスト項目の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        list_id: int,
        title: str,
        status: str = "pending",
    ) -> ListItemEntity:
        """リスト項目を作成"""
        list_item = ListItem(
            list_id=list_id,
            title=title,
            status=status,
        )

        self._session.add(list_item)
        await self._session.flush()
        await self._session.refresh(list_item)

        return self._to_entity(list_item)

    async def find_by_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> ListItemEntity | None:
        """IDでリスト項目を検索（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItem)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItem.id == list_item_id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        list_item = result.scalar_one_or_none()

        if list_item is None:
            return None

        return self._to_entity(list_item)

    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ListItemEntity]:
        """リストに属するリスト項目の一覧を取得（マルチテナント対応）"""
        # list_item -> list -> organizationを経由してテナント分離
        conditions = [
            ListItem.list_id == list_id,
            List.organization_id == requesting_organization_id,
        ]
        if not include_deleted:
            conditions.append(ListItem.deleted_at.is_(None))

        stmt = (
            select(ListItem)
            .join(List, ListItem.list_id == List.id)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(ListItem.created_at.desc())
        )

        result = await self._session.execute(stmt)
        list_items = result.scalars().all()

        return [self._to_entity(item) for item in list_items]

    async def update(
        self,
        list_item: ListItemEntity,
        requesting_organization_id: int,
    ) -> ListItemEntity:
        """リスト項目情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItem)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItem.id == list_item.id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_list_item = result.scalar_one_or_none()

        if db_list_item is None:
            raise ListItemNotFoundError(list_item.id)

        # エンティティの値でモデルを更新
        db_list_item.title = list_item.title
        db_list_item.status = list_item.status

        await self._session.flush()
        await self._session.refresh(db_list_item)

        return self._to_entity(db_list_item)

    async def soft_delete(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> None:
        """リスト項目を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItem)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItem.id == list_item_id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        list_item = result.scalar_one_or_none()

        if list_item is None:
            raise ListItemNotFoundError(list_item_id)

        list_item.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(self, list_item: ListItem) -> ListItemEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ListItemEntity(
            id=list_item.id,
            list_id=list_item.list_id,
            title=list_item.title,
            status=list_item.status,
            created_at=list_item.created_at,
            updated_at=list_item.updated_at,
            deleted_at=list_item.deleted_at,
        )
