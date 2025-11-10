"""
顧客組織リポジトリの実装

IClientOrganizationRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.client_organization_entity import ClientOrganizationEntity
from src.domain.exceptions import ClientOrganizationNotFoundError
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)
from src.infrastructure.persistence.models.client_organization import (
    ClientOrganization,
)
from src.infrastructure.persistence.models.organization import Organization


class ClientOrganizationRepository(IClientOrganizationRepository):
    """
    顧客組織リポジトリの実装

    SQLAlchemyを使用して顧客組織の永続化を行います。
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
        industry: str | None = None,
        employee_count: int | None = None,
        annual_revenue: int | None = None,
        established_year: int | None = None,
        website: str | None = None,
        sales_person: str | None = None,
        notes: str | None = None,
    ) -> ClientOrganizationEntity:
        """顧客組織を作成"""
        client_org = ClientOrganization(
            organization_id=organization_id,
            industry=industry,
            employee_count=employee_count,
            annual_revenue=annual_revenue,
            established_year=established_year,
            website=website,
            sales_person=sales_person,
            notes=notes,
        )

        self._session.add(client_org)
        await self._session.flush()
        await self._session.refresh(client_org)

        return self._to_entity(client_org)

    async def find_by_id(
        self, client_organization_id: int
    ) -> ClientOrganizationEntity | None:
        """IDで顧客組織を検索"""
        stmt = select(ClientOrganization).where(
            ClientOrganization.id == client_organization_id,
            ClientOrganization.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        client_org = result.scalar_one_or_none()

        if client_org is None:
            return None

        return self._to_entity(client_org)

    async def find_by_organization_id(
        self, organization_id: int
    ) -> ClientOrganizationEntity | None:
        """組織IDで顧客組織を検索"""
        stmt = select(ClientOrganization).where(
            ClientOrganization.organization_id == organization_id,
            ClientOrganization.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        client_org = result.scalar_one_or_none()

        if client_org is None:
            return None

        return self._to_entity(client_org)

    async def list_by_sales_support_organization(
        self,
        sales_support_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ClientOrganizationEntity]:
        """営業支援会社に属する顧客組織の一覧を取得"""
        # ClientOrganization -> Organization -> parent_organization_id で検索
        conditions = [
            Organization.parent_organization_id == sales_support_organization_id,
        ]
        if not include_deleted:
            conditions.append(ClientOrganization.deleted_at.is_(None))
            conditions.append(Organization.deleted_at.is_(None))

        stmt = (
            select(ClientOrganization)
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(ClientOrganization.created_at.desc())
        )

        result = await self._session.execute(stmt)
        client_orgs = result.scalars().all()

        return [self._to_entity(co) for co in client_orgs]

    async def update(
        self, client_organization: ClientOrganizationEntity
    ) -> ClientOrganizationEntity:
        """顧客組織情報を更新"""
        stmt = select(ClientOrganization).where(
            ClientOrganization.id == client_organization.id,
            ClientOrganization.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_client_org = result.scalar_one_or_none()

        if db_client_org is None:
            raise ClientOrganizationNotFoundError(client_organization.id)

        # エンティティの値でモデルを更新
        db_client_org.industry = client_organization.industry
        db_client_org.employee_count = client_organization.employee_count
        db_client_org.annual_revenue = client_organization.annual_revenue
        db_client_org.established_year = client_organization.established_year
        db_client_org.website = client_organization.website
        db_client_org.sales_person = client_organization.sales_person
        db_client_org.notes = client_organization.notes

        await self._session.flush()
        await self._session.refresh(db_client_org)

        return self._to_entity(db_client_org)

    async def soft_delete(self, client_organization_id: int) -> None:
        """顧客組織を論理削除（ソフトデリート）"""
        stmt = select(ClientOrganization).where(
            ClientOrganization.id == client_organization_id,
            ClientOrganization.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        client_org = result.scalar_one_or_none()

        if client_org is None:
            raise ClientOrganizationNotFoundError(client_organization_id)

        client_org.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(
        self, client_org: ClientOrganization
    ) -> ClientOrganizationEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ClientOrganizationEntity(
            id=client_org.id,
            organization_id=client_org.organization_id,
            industry=client_org.industry,
            employee_count=client_org.employee_count,
            annual_revenue=client_org.annual_revenue,
            established_year=client_org.established_year,
            website=client_org.website,
            sales_person=client_org.sales_person,
            notes=client_org.notes,
            created_at=client_org.created_at,
            updated_at=client_org.updated_at,
            deleted_at=client_org.deleted_at,
        )
