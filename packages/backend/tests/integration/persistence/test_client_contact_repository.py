"""
顧客担当者リポジトリの結合テスト

実際のデータベースを使用してClientContactRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ClientContactNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.client_contact_repository import (
    ClientContactRepository,
)
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


@pytest.fixture
async def test_client_organization(
    db_session: AsyncSession, client_base_organization: Organization
):
    """テスト用顧客組織を作成"""
    repo = ClientOrganizationRepository(db_session)
    return await repo.create(
        organization_id=client_base_organization.id,
        industry="IT・情報通信",
        employee_count=500,
    )


class TestClientContactRepositoryCreate:
    """顧客担当者作成のテスト"""

    async def test_create_client_contact_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：顧客担当者を作成できる"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # Act
        contact = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="山田太郎",
            department="営業部",
            position="部長",
            email="yamada@example.com",
            phone="03-1234-5678",
            mobile="090-1234-5678",
            is_primary=True,
            notes="窓口担当者",
        )

        # Assert
        assert contact.id > 0
        assert contact.client_organization_id == test_client_organization.id
        assert contact.full_name == "山田太郎"
        assert contact.department == "営業部"
        assert contact.position == "部長"
        assert contact.email == "yamada@example.com"
        assert contact.phone == "03-1234-5678"
        assert contact.mobile == "090-1234-5678"
        assert contact.is_primary is True
        assert contact.notes == "窓口担当者"

    async def test_create_client_contact_minimal(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：必須項目のみで顧客担当者を作成できる"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # Act
        contact = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="佐藤花子",
        )

        # Assert
        assert contact.id > 0
        assert contact.full_name == "佐藤花子"
        assert contact.department is None
        assert contact.position is None
        assert contact.is_primary is False


class TestClientContactRepositoryFind:
    """顧客担当者検索のテスト"""

    async def test_find_by_id_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：IDで顧客担当者を検索できる"""
        # Arrange
        repo = ClientContactRepository(db_session)
        created = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="田中一郎",
            email="tanaka@example.com",
        )

        # Act
        contact = await repo.find_by_id(created.id)

        # Assert
        assert contact is not None
        assert contact.id == created.id
        assert contact.full_name == "田中一郎"
        assert contact.email == "tanaka@example.com"

    async def test_find_by_id_not_found(self, db_session: AsyncSession) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # Act
        contact = await repo.find_by_id(999999)

        # Assert
        assert contact is None

    async def test_list_by_client_organization_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：顧客組織IDで担当者一覧を取得できる"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # 3人の担当者を作成
        for i in range(3):
            await repo.create(
                client_organization_id=test_client_organization.id,
                full_name=f"担当者{i+1}",
                email=f"contact{i+1}@example.com",
            )

        # Act
        contacts = await repo.list_by_client_organization(test_client_organization.id)

        # Assert
        assert len(contacts) == 3
        assert all(c.full_name in ["担当者1", "担当者2", "担当者3"] for c in contacts)

    async def test_find_primary_contact_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：主担当者を取得できる"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # 複数の担当者を作成（1人だけis_primary=True）
        await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="副担当者",
            is_primary=False,
        )
        primary = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="主担当者",
            is_primary=True,
        )

        # Act
        found = await repo.find_primary_contact(test_client_organization.id)

        # Assert
        assert found is not None
        assert found.id == primary.id
        assert found.full_name == "主担当者"
        assert found.is_primary is True

    async def test_find_primary_contact_not_found(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：主担当者が存在しない場合はNoneを返す"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # 主担当者以外を作成
        await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="副担当者",
            is_primary=False,
        )

        # Act
        found = await repo.find_primary_contact(test_client_organization.id)

        # Assert
        assert found is None


class TestClientContactRepositoryUpdate:
    """顧客担当者更新のテスト"""

    async def test_update_client_contact_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：顧客担当者を更新できる"""
        # Arrange
        repo = ClientContactRepository(db_session)
        contact = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="山田太郎",
            department="営業部",
            position="課長",
        )

        # Act
        contact.position = "部長"
        contact.email = "yamada.updated@example.com"
        contact.notes = "昇進しました"
        updated = await repo.update(contact)

        # Assert
        assert updated.id == contact.id
        assert updated.position == "部長"
        assert updated.email == "yamada.updated@example.com"
        assert updated.notes == "昇進しました"

    async def test_update_client_contact_not_found(self, db_session: AsyncSession) -> None:
        """異常系：存在しない顧客担当者の更新でエラー"""
        # Arrange
        repo = ClientContactRepository(db_session)
        from src.domain.entities.client_contact_entity import ClientContactEntity

        fake_entity = ClientContactEntity(
            id=999999,
            client_organization_id=1,
            full_name="存在しない",
            is_primary=False,
        )

        # Act & Assert
        with pytest.raises(ClientContactNotFoundError):
            await repo.update(fake_entity)


class TestClientContactRepositorySoftDelete:
    """顧客担当者論理削除のテスト"""

    async def test_soft_delete_success(
        self, db_session: AsyncSession, test_client_organization
    ) -> None:
        """正常系：顧客担当者を論理削除できる"""
        # Arrange
        repo = ClientContactRepository(db_session)
        contact = await repo.create(
            client_organization_id=test_client_organization.id,
            full_name="山田太郎",
        )

        # Act
        await repo.soft_delete(contact.id)

        # Assert
        deleted = await repo.find_by_id(contact.id)
        assert deleted is None

    async def test_soft_delete_not_found(self, db_session: AsyncSession) -> None:
        """異常系：存在しない顧客担当者の論理削除でエラー"""
        # Arrange
        repo = ClientContactRepository(db_session)

        # Act & Assert
        with pytest.raises(ClientContactNotFoundError):
            await repo.soft_delete(999999)
