"""
リストスクリプトリポジトリの実装

IListScriptRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.list_script_entity import ListScriptEntity
from src.domain.interfaces.list_script_repository import IListScriptRepository
from src.infrastructure.persistence.models.list_script import ListScript


class ListScriptRepository(IListScriptRepository):
    """
    リストスクリプトリポジトリの実装

    SQLAlchemyを使用してスクリプトの永続化を行います。
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
        content: str,
    ) -> ListScriptEntity:
        """スクリプトを作成"""
        script_model = ListScript(
            list_id=list_id,
            title=title,
            content=content,
        )

        self._session.add(script_model)
        await self._session.flush()
        await self._session.refresh(script_model)

        return self._to_entity(script_model)

    async def get_by_id(self, script_id: int) -> ListScriptEntity | None:
        """IDでスクリプトを取得"""
        stmt = select(ListScript).where(
            ListScript.id == script_id,
            ListScript.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        script_model = result.scalar_one_or_none()

        if script_model is None:
            return None

        return self._to_entity(script_model)

    async def list_by_list_id(self, list_id: int) -> list[ListScriptEntity]:
        """リストIDでスクリプト一覧を取得"""
        stmt = (
            select(ListScript)
            .where(
                ListScript.list_id == list_id,
                ListScript.deleted_at.is_(None),
            )
            .order_by(ListScript.created_at.desc())
        )
        result = await self._session.execute(stmt)
        scripts = result.scalars().all()

        return [self._to_entity(script) for script in scripts]

    async def update(
        self,
        script_id: int,
        title: str | None = None,
        content: str | None = None,
    ) -> ListScriptEntity | None:
        """スクリプトを更新"""
        stmt = select(ListScript).where(
            ListScript.id == script_id,
            ListScript.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        script_model = result.scalar_one_or_none()

        if script_model is None:
            return None

        # 部分更新をサポート
        if title is not None:
            script_model.title = title
        if content is not None:
            script_model.content = content

        await self._session.flush()
        await self._session.refresh(script_model)

        return self._to_entity(script_model)

    async def delete(self, script_id: int) -> bool:
        """スクリプトを論理削除（ソフトデリート）"""
        stmt = select(ListScript).where(
            ListScript.id == script_id,
            ListScript.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        script_model = result.scalar_one_or_none()

        if script_model is None:
            return False

        script_model.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        return True

    async def exists(self, script_id: int) -> bool:
        """スクリプトが存在するかチェック"""
        stmt = select(ListScript.id).where(
            ListScript.id == script_id,
            ListScript.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, script_model: ListScript) -> ListScriptEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ListScriptEntity(
            id=script_model.id,
            list_id=script_model.list_id,
            title=script_model.title,
            content=script_model.content,
            created_at=script_model.created_at,
            updated_at=script_model.updated_at,
            deleted_at=script_model.deleted_at,
        )
