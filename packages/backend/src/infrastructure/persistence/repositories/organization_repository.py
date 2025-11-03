"""
組織リポジトリの実装

営業支援会社組織と顧客組織の管理を行うリポジトリ実装
"""

from datetime import datetime, timezone
from typing import Sequence


from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import OrganizationNotFoundException
from src.domain.interfaces.organization_repository import IOrganizationRepository
from src.infrastructure.persistence.models.organization import Organization


class OrganizationRepository(IOrganizationRepository):
    """組織リポジトリの実装クラス"""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: SQLAlchemyの非同期セッション
        """
        self._session = session

    async def create(self, organization: Organization) -> Organization:
        """
        新規組織を作成

        Args:
            organization: 作成する組織エンティティ

        Returns:
            作成された組織
        """
        self._session.add(organization)
        await self._session.flush()
        await self._session.refresh(organization)
        return organization

    async def find_by_id(self, organization_id: int) -> Organization | None:
        """
        IDで組織を検索

        Args:
            organization_id: 組織ID

        Returns:
            見つかった組織、存在しない場合はNone
        """
        stmt = select(Organization).where(
            and_(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[Organization]:
        """
        全組織一覧を取得

        Args:
            skip: スキップする件数
            limit: 取得する最大件数
            include_deleted: 論理削除された組織を含むか

        Returns:
            組織のリスト
        """
        conditions = []

        if not include_deleted:
            conditions.append(Organization.deleted_at.is_(None))

        stmt = (
            select(Organization)
            .where(and_(*conditions) if conditions else True)
            .offset(skip)
            .limit(limit)
            .order_by(Organization.created_at.desc())
        )

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_parent(
        self,
        parent_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[Organization]:
        """
        親組織に紐づく子組織一覧を取得（顧客組織の取得）

        Args:
            parent_organization_id: 親組織ID
            skip: スキップする件数
            limit: 取得する最大件数
            include_deleted: 論理削除された組織を含むか

        Returns:
            子組織のリスト
        """
        conditions = [Organization.parent_organization_id == parent_organization_id]

        if not include_deleted:
            conditions.append(Organization.deleted_at.is_(None))

        stmt = (
            select(Organization)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Organization.created_at.desc())
        )

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, organization: Organization) -> Organization:
        """
        組織情報を更新

        Args:
            organization: 更新する組織エンティティ

        Returns:
            更新された組織

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
        """
        # 更新日時を設定
        organization.updated_at = datetime.now(timezone.utc)

        await self._session.flush()
        await self._session.refresh(organization)
        return organization

    async def soft_delete(self, organization_id: int) -> None:
        """
        組織を論理削除

        Args:
            organization_id: 組織ID

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
        """
        organization = await self.find_by_id(organization_id)

        if organization is None:
            raise OrganizationNotFoundException(organization_id=str(organization_id))

        # 論理削除
        organization.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def count_all(self, include_deleted: bool = False) -> int:
        """
        組織の総数を取得

        Args:
            include_deleted: 論理削除された組織を含むか

        Returns:
            組織数
        """
        conditions = []

        if not include_deleted:
            conditions.append(Organization.deleted_at.is_(None))

        stmt = select(func.count(Organization.id)).where(
            and_(*conditions) if conditions else True
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
