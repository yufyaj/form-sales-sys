"""
リストリポジトリの実装

IListRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.list_entity import ListEntity
from src.domain.exceptions import ListNotFoundError
from src.domain.interfaces.list_repository import IListRepository
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.organization import Organization


class ListRepository(IListRepository):
    """
    リストリポジトリの実装

    SQLAlchemyを使用してリストの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        organization_id: int,
        name: str,
        description: str | None = None,
    ) -> ListEntity:
        """リストを作成"""
        list_model = List(
            organization_id=organization_id,
            name=name,
            description=description,
        )

        self._session.add(list_model)
        await self._session.flush()
        await self._session.refresh(list_model)

        return self._to_entity(list_model)

    async def find_by_id(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity | None:
        """IDでリストを検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = (
            select(List)
            .where(
                List.id == list_id,
                List.organization_id == requesting_organization_id,
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        list_model = result.scalar_one_or_none()

        if list_model is None:
            return None

        return self._to_entity(list_model)

    async def list_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ListEntity]:
        """組織に属するリストの一覧を取得"""
        conditions = [
            List.organization_id == organization_id,
        ]
        if not include_deleted:
            conditions.append(List.deleted_at.is_(None))

        stmt = (
            select(List)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(List.created_at.desc())
        )

        result = await self._session.execute(stmt)
        lists = result.scalars().all()

        return [self._to_entity(lst) for lst in lists]

    async def update(
        self,
        list_entity: ListEntity,
        requesting_organization_id: int,
    ) -> ListEntity:
        """リスト情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = (
            select(List)
            .where(
                List.id == list_entity.id,
                List.organization_id == requesting_organization_id,
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_list = result.scalar_one_or_none()

        if db_list is None:
            raise ListNotFoundError(list_entity.id)

        # エンティティの値でモデルを更新
        db_list.name = list_entity.name
        db_list.description = list_entity.description

        await self._session.flush()
        await self._session.refresh(db_list)

        return self._to_entity(db_list)

    async def soft_delete(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> None:
        """リストを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = (
            select(List)
            .where(
                List.id == list_id,
                List.organization_id == requesting_organization_id,
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        list_model = result.scalar_one_or_none()

        if list_model is None:
            raise ListNotFoundError(list_id)

        list_model.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def duplicate(
        self,
        source_list_id: int,
        new_name: str,
        requesting_organization_id: int,
    ) -> ListEntity:
        """リストを複製（マルチテナント対応・IDOR脆弱性対策）"""
        # 複製元のリストを取得
        stmt = (
            select(List)
            .where(
                List.id == source_list_id,
                List.organization_id == requesting_organization_id,
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        source_list = result.scalar_one_or_none()

        if source_list is None:
            raise ListNotFoundError(source_list_id)

        # 新しいリストを作成
        new_list = List(
            organization_id=source_list.organization_id,
            name=new_name,
            description=source_list.description,
        )

        self._session.add(new_list)
        await self._session.flush()
        await self._session.refresh(new_list)

        # リストアイテムを複製
        # lazy loadingを避けるため、明示的にクエリを発行
        from src.infrastructure.persistence.models.list_item import ListItem
        from src.infrastructure.persistence.models.list_item_custom_value import (
            ListItemCustomValue,
        )

        stmt_items = select(ListItem).where(
            ListItem.list_id == source_list_id,
            ListItem.deleted_at.is_(None),
        )
        result_items = await self._session.execute(stmt_items)
        source_items = result_items.scalars().all()

        # 各リストアイテムとそのカスタム値を複製
        for source_item in source_items:
            # 新しいリストアイテムを作成
            new_item = ListItem(
                list_id=new_list.id,
                title=source_item.title,
                status=source_item.status,
            )
            self._session.add(new_item)
            await self._session.flush()
            await self._session.refresh(new_item)

            # カスタム値を複製
            stmt_values = select(ListItemCustomValue).where(
                ListItemCustomValue.list_item_id == source_item.id,
                ListItemCustomValue.deleted_at.is_(None),
            )
            result_values = await self._session.execute(stmt_values)
            source_values = result_values.scalars().all()

            for source_value in source_values:
                new_value = ListItemCustomValue(
                    list_item_id=new_item.id,
                    custom_column_setting_id=source_value.custom_column_setting_id,
                    value=source_value.value,
                )
                self._session.add(new_value)

        await self._session.flush()
        await self._session.refresh(new_list)

        return self._to_entity(new_list)

    def _to_entity(self, list_model: List) -> ListEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ListEntity(
            id=list_model.id,
            organization_id=list_model.organization_id,
            name=list_model.name,
            description=list_model.description,
            created_at=list_model.created_at,
            updated_at=list_model.updated_at,
            deleted_at=list_model.deleted_at,
        )
