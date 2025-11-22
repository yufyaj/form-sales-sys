"""
リストリポジトリの実装

IListRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.list_entity import ListEntity, ListStatus
from src.domain.exceptions import ListNotFoundError
from src.domain.interfaces.list_repository import IListRepository
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.organization import Organization

logger = logging.getLogger(__name__)


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
        """
        リストを複製（マルチテナント対応・IDOR脆弱性対策）

        Note:
            この操作はトランザクション内で実行される必要があります。
            複製中にエラーが発生した場合、全ての変更がロールバックされます。
            パフォーマンス最適化のため、eager loadingを使用してN+1問題を回避しています。
        """
        logger.info(
            "Duplicating list",
            extra={
                "source_list_id": source_list_id,
                "organization_id": requesting_organization_id,
                "new_name": new_name,
            },
        )

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
            logger.warning(
                "List not found for duplication",
                extra={
                    "source_list_id": source_list_id,
                    "organization_id": requesting_organization_id,
                },
            )
            raise ListNotFoundError(source_list_id)

        # 新しいリストを作成（防御的プログラミング: 明示的にrequesting_organization_idを使用）
        new_list = List(
            organization_id=requesting_organization_id,
            name=new_name,
            description=source_list.description,
        )

        self._session.add(new_list)
        await self._session.flush()
        await self._session.refresh(new_list)

        # リストアイテムとカスタム値を一括取得（N+1問題の回避）
        from src.infrastructure.persistence.models.list_item import ListItem
        from src.infrastructure.persistence.models.list_item_custom_value import (
            ListItemCustomValue,
        )

        # eager loadingでカスタム値も一緒に取得
        stmt_items = (
            select(ListItem)
            .options(selectinload(ListItem.custom_values))
            .where(
                ListItem.list_id == source_list_id,
                ListItem.deleted_at.is_(None),
            )
        )
        result_items = await self._session.execute(stmt_items)
        source_items = result_items.scalars().all()

        # リストアイテムをバッチ処理で複製
        new_items = []
        for source_item in source_items:
            new_item = ListItem(
                list_id=new_list.id,
                title=source_item.title,
                status=source_item.status,
            )
            new_items.append(new_item)
            self._session.add(new_item)

        # 全リストアイテムを一括flush
        if new_items:
            await self._session.flush()

        # カスタム値を複製（IDが割り当てられた後）
        custom_values_count = 0
        for idx, source_item in enumerate(source_items):
            new_item = new_items[idx]
            for source_value in source_item.custom_values:
                # 論理削除されていないカスタム値のみ複製
                if source_value.deleted_at is None:
                    new_value = ListItemCustomValue(
                        list_item_id=new_item.id,
                        custom_column_setting_id=source_value.custom_column_setting_id,
                        value=source_value.value,
                    )
                    self._session.add(new_value)
                    custom_values_count += 1

        await self._session.flush()
        await self._session.refresh(new_list)

        logger.info(
            "List duplicated successfully",
            extra={
                "source_list_id": source_list_id,
                "new_list_id": new_list.id,
                "items_count": len(source_items),
                "custom_values_count": custom_values_count,
            },
        )

        return self._to_entity(new_list)

    async def update_status(
        self,
        list_id: int,
        status: ListStatus,
        requesting_organization_id: int,
    ) -> ListEntity:
        """リストステータスを更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = (
            select(List)
            .where(
                List.id == list_id,
                List.organization_id == requesting_organization_id,
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_list = result.scalar_one_or_none()

        if db_list is None:
            raise ListNotFoundError(list_id)

        # ステータスを更新
        db_list.status = status

        await self._session.flush()
        await self._session.refresh(db_list)

        return self._to_entity(db_list)

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
            status=list_model.status,
            created_at=list_model.created_at,
            updated_at=list_model.updated_at,
            deleted_at=list_model.deleted_at,
        )
