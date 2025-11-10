"""
顧客組織リポジトリの結合テスト

実際のデータベースを使用してClientOrganizationRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ClientOrganizationNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.client_organization_repository import (
    ClientOrganizationRepository,
)


@pytest.fixture
async def sales_support_organization(db_session: AsyncSession) -> Organization:
    """テスト用営業支援会社組織を作成"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def client_base_organization(
    db_session: AsyncSession, sales_support_organization: Organization
) -> Organization:
    """テスト用顧客企業の基本組織を作成"""
    org = Organization(
        name="テスト顧客企業",
        type=OrganizationType.CLIENT,
        parent_organization_id=sales_support_organization.id,
        email="client@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


class TestClientOrganizationRepositoryCreate:
    """顧客組織作成のテスト"""

    async def test_create_client_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_base_organization: Organization,
    ) -> None:
        """正常系：顧客組織を作成できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # Act
        client_org = await repo.create(
            organization_id=client_base_organization.id,
            industry="IT・情報通信",
            employee_count=500,
            annual_revenue=1000000000,
            established_year=2010,
            website="https://example.com",
            sales_person="山田太郎",
            notes="重要顧客",
        )

        # Assert
        assert client_org.id > 0
        assert client_org.organization_id == client_base_organization.id
        assert client_org.industry == "IT・情報通信"
        assert client_org.employee_count == 500
        assert client_org.annual_revenue == 1000000000
        assert client_org.established_year == 2010
        assert client_org.website == "https://example.com"
        assert client_org.sales_person == "山田太郎"
        assert client_org.notes == "重要顧客"

    async def test_create_client_organization_minimal(
        self,
        db_session: AsyncSession,
        client_base_organization: Organization,
    ) -> None:
        """正常系：必須項目のみで顧客組織を作成できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # Act
        client_org = await repo.create(
            organization_id=client_base_organization.id,
        )

        # Assert
        assert client_org.id > 0
        assert client_org.organization_id == client_base_organization.id
        assert client_org.industry is None
        assert client_org.employee_count is None


class TestClientOrganizationRepositoryFind:
    """顧客組織検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        client_base_organization: Organization,
    ) -> None:
        """正常系：IDで顧客組織を検索できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        created = await repo.create(
            organization_id=client_base_organization.id,
            industry="製造業",
            employee_count=1000,
        )

        # Act
        client_org = await repo.find_by_id(created.id)

        # Assert
        assert client_org is not None
        assert client_org.id == created.id
        assert client_org.industry == "製造業"
        assert client_org.employee_count == 1000

    async def test_find_by_id_not_found(self, db_session: AsyncSession) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # Act
        client_org = await repo.find_by_id(999999)

        # Assert
        assert client_org is None

    async def test_find_by_organization_id_success(
        self,
        db_session: AsyncSession,
        client_base_organization: Organization,
    ) -> None:
        """正常系：組織IDで顧客組織を検索できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        await repo.create(
            organization_id=client_base_organization.id,
            industry="小売業",
        )

        # Act
        client_org = await repo.find_by_organization_id(client_base_organization.id)

        # Assert
        assert client_org is not None
        assert client_org.organization_id == client_base_organization.id
        assert client_org.industry == "小売業"

    async def test_list_by_sales_support_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：営業支援会社IDで顧客組織一覧を取得できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # 3つの顧客組織を作成
        for i in range(3):
            client_org = Organization(
                name=f"顧客企業{i+1}",
                type=OrganizationType.CLIENT,
                parent_organization_id=sales_support_organization.id,
            )
            db_session.add(client_org)
            await db_session.flush()
            await repo.create(
                organization_id=client_org.id,
                industry=f"業種{i+1}",
            )

        # Act
        client_orgs = await repo.list_by_sales_support_organization(
            sales_support_organization.id
        )

        # Assert
        assert len(client_orgs) == 3
        assert all(co.industry in ["業種1", "業種2", "業種3"] for co in client_orgs)


class TestClientOrganizationRepositoryUpdate:
    """顧客組織更新のテスト"""

    async def test_update_client_organization_success(
        self,
        db_session: AsyncSession,
        client_base_organization: Organization,
    ) -> None:
        """正常系：顧客組織を更新できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        client_org = await repo.create(
            organization_id=client_base_organization.id,
            industry="IT・情報通信",
            employee_count=500,
        )

        # Act
        client_org.industry = "製造業"
        client_org.employee_count = 1000
        client_org.notes = "業種変更"
        updated = await repo.update(client_org)

        # Assert
        assert updated.id == client_org.id
        assert updated.industry == "製造業"
        assert updated.employee_count == 1000
        assert updated.notes == "業種変更"

    async def test_update_client_organization_not_found(
        self, db_session: AsyncSession
    ) -> None:
        """異常系：存在しない顧客組織の更新でエラー"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        from src.domain.entities.client_organization_entity import (
            ClientOrganizationEntity,
        )

        fake_entity = ClientOrganizationEntity(
            id=999999,
            organization_id=1,
            industry="存在しない",
        )

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.update(fake_entity)


class TestClientOrganizationRepositorySoftDelete:
    """顧客組織論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        client_base_organization: Organization,
    ) -> None:
        """正常系：顧客組織を論理削除できる"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        client_org = await repo.create(
            organization_id=client_base_organization.id,
            industry="IT・情報通信",
        )

        # Act
        await repo.soft_delete(client_org.id)

        # Assert
        deleted = await repo.find_by_id(client_org.id)
        assert deleted is None

    async def test_soft_delete_not_found(self, db_session: AsyncSession) -> None:
        """異常系：存在しない顧客組織の論理削除でエラー"""
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.soft_delete(999999)
