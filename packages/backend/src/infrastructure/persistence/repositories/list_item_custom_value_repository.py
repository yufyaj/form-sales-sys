"""
リスト項目カスタム値リポジトリの実装

IListItemCustomValueRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.list_item_custom_value_entity import (
    ListItemCustomValueEntity,
)
from src.domain.exceptions import ListItemCustomValueNotFoundError
from src.domain.interfaces.list_item_custom_value_repository import (
    IListItemCustomValueRepository,
)
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.list_item import ListItem
from src.infrastructure.persistence.models.list_item_custom_value import (
    ListItemCustomValue,
)


class ListItemCustomValueRepository(IListItemCustomValueRepository):
    """
    リスト項目カスタム値リポジトリの実装

    SQLAlchemyを使用してリスト項目カスタム値の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        list_item_id: int,
        custom_column_setting_id: int,
        value: dict | None = None,
    ) -> ListItemCustomValueEntity:
        """リスト項目カスタム値を作成"""
        custom_value = ListItemCustomValue(
            list_item_id=list_item_id,
            custom_column_setting_id=custom_column_setting_id,
            value=value,
        )

        self._session.add(custom_value)
        await self._session.flush()
        await self._session.refresh(custom_value)

        return self._to_entity(custom_value)

    async def find_by_id(
        self,
        list_item_custom_value_id: int,
        requesting_organization_id: int,
    ) -> ListItemCustomValueEntity | None:
        """IDでリスト項目カスタム値を検索（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item_custom_value -> list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItemCustomValue)
            .join(ListItem, ListItemCustomValue.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemCustomValue.id == list_item_custom_value_id,
                List.organization_id == requesting_organization_id,
                ListItemCustomValue.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        custom_value = result.scalar_one_or_none()

        if custom_value is None:
            return None

        return self._to_entity(custom_value)

    async def list_by_list_item_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[ListItemCustomValueEntity]:
        """リスト項目に属するカスタム値の一覧を取得（マルチテナント対応）"""
        # list_item_custom_value -> list_item -> list -> organizationを経由してテナント分離
        conditions = [
            ListItemCustomValue.list_item_id == list_item_id,
            List.organization_id == requesting_organization_id,
        ]
        if not include_deleted:
            conditions.append(ListItemCustomValue.deleted_at.is_(None))

        stmt = (
            select(ListItemCustomValue)
            .join(ListItem, ListItemCustomValue.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(and_(*conditions))
            .order_by(ListItemCustomValue.created_at.asc())
        )

        result = await self._session.execute(stmt)
        custom_values = result.scalars().all()

        return [self._to_entity(cv) for cv in custom_values]

    async def update(
        self,
        list_item_custom_value: ListItemCustomValueEntity,
        requesting_organization_id: int,
    ) -> ListItemCustomValueEntity:
        """リスト項目カスタム値を更新（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item_custom_value -> list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItemCustomValue)
            .join(ListItem, ListItemCustomValue.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemCustomValue.id == list_item_custom_value.id,
                List.organization_id == requesting_organization_id,
                ListItemCustomValue.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_custom_value = result.scalar_one_or_none()

        if db_custom_value is None:
            raise ListItemCustomValueNotFoundError(list_item_custom_value.id)

        # エンティティの値でモデルを更新
        db_custom_value.value = list_item_custom_value.value

        await self._session.flush()
        await self._session.refresh(db_custom_value)

        return self._to_entity(db_custom_value)

    async def soft_delete(
        self,
        list_item_custom_value_id: int,
        requesting_organization_id: int,
    ) -> None:
        """リスト項目カスタム値を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        # list_item_custom_value -> list_item -> list -> organizationを経由してテナント分離
        stmt = (
            select(ListItemCustomValue)
            .join(ListItem, ListItemCustomValue.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemCustomValue.id == list_item_custom_value_id,
                List.organization_id == requesting_organization_id,
                ListItemCustomValue.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        custom_value = result.scalar_one_or_none()

        if custom_value is None:
            raise ListItemCustomValueNotFoundError(list_item_custom_value_id)

        custom_value.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(
        self, custom_value: ListItemCustomValue
    ) -> ListItemCustomValueEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ListItemCustomValueEntity(
            id=custom_value.id,
            list_item_id=custom_value.list_item_id,
            custom_column_setting_id=custom_value.custom_column_setting_id,
            value=custom_value.value,
            created_at=custom_value.created_at,
            updated_at=custom_value.updated_at,
            deleted_at=custom_value.deleted_at,
        )
