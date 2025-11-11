"""
顧客管理APIのセキュリティテスト

IDOR（Insecure Direct Object Reference）攻撃に対する防御をテストします。
マルチテナント環境で、他のテナントのリソースにアクセスできないことを確認します。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ClientOrganizationNotFoundError, ClientContactNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.client_contact_repository import (
    ClientContactRepository,
)
from src.infrastructure.persistence.repositories.client_organization_repository import (
    ClientOrganizationRepository,
)


@pytest.fixture
async def sales_support_org_a(db_session: AsyncSession) -> Organization:
    """営業支援会社A（正当なテナント）"""
    org = Organization(
        name="営業支援会社A",
        type=OrganizationType.SALES_SUPPORT,
        email="sales_a@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def sales_support_org_b(db_session: AsyncSession) -> Organization:
    """営業支援会社B（別のテナント・攻撃者）"""
    org = Organization(
        name="営業支援会社B",
        type=OrganizationType.SALES_SUPPORT,
        email="sales_b@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def client_org_of_a(
    db_session: AsyncSession, sales_support_org_a: Organization
) -> Organization:
    """営業支援会社Aの顧客組織"""
    org = Organization(
        name="Aの顧客企業",
        type=OrganizationType.CLIENT,
        parent_organization_id=sales_support_org_a.id,
        email="client_a@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def client_org_of_b(
    db_session: AsyncSession, sales_support_org_b: Organization
) -> Organization:
    """営業支援会社Bの顧客組織"""
    org = Organization(
        name="Bの顧客企業",
        type=OrganizationType.CLIENT,
        parent_organization_id=sales_support_org_b.id,
        email="client_b@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


class TestClientOrganizationIDORAttack:
    """顧客組織のIDOR攻撃テスト"""

    async def test_cannot_read_other_tenant_client_organization(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
        client_org_of_b: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客組織を読み取れないこと

        攻撃シナリオ：
        - 営業支援会社Bが、営業支援会社Aの顧客組織IDを推測
        - 営業支援会社Bが営業支援会社Aの顧客組織にアクセスを試みる

        期待結果：
        - アクセスが拒否される（Noneを返す）
        """
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # 営業支援会社Aの顧客組織を作成
        client_org_a = await repo.create(
            organization_id=client_org_of_a.id,
            industry="IT・情報通信",
            notes="Aの重要顧客",
        )

        # Act: 営業支援会社BがAの顧客組織にアクセスを試みる（IDOR攻撃）
        stolen_data = await repo.find_by_id(
            client_org_a.id, sales_support_org_b.id  # ← 別のテナントIDを使用
        )

        # Assert: アクセスが拒否される
        assert stolen_data is None, "🚨 IDOR脆弱性: 他のテナントのデータにアクセスできてしまう！"

    async def test_cannot_update_other_tenant_client_organization(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客組織を更新できないこと

        攻撃シナリオ：
        - 営業支援会社Bが、営業支援会社Aの顧客組織を更新しようとする

        期待結果：
        - 例外が発生する
        """
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        client_org_a = await repo.create(
            organization_id=client_org_of_a.id,
            industry="IT・情報通信",
        )

        # Act & Assert: 営業支援会社BがAの顧客組織を更新しようとする
        client_org_a.industry = "悪意のある更新"
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.update(client_org_a, sales_support_org_b.id)

    async def test_cannot_delete_other_tenant_client_organization(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客組織を削除できないこと

        攻撃シナリオ：
        - 営業支援会社Bが、営業支援会社Aの顧客組織を削除しようとする

        期待結果：
        - 例外が発生する
        """
        # Arrange
        repo = ClientOrganizationRepository(db_session)
        client_org_a = await repo.create(
            organization_id=client_org_of_a.id,
            industry="IT・情報通信",
        )

        # Act & Assert: 営業支援会社BがAの顧客組織を削除しようとする
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.soft_delete(client_org_a.id, sales_support_org_b.id)

        # 営業支援会社Aは自分の顧客組織を取得できることを確認
        result = await repo.find_by_id(client_org_a.id, sales_support_org_a.id)
        assert result is not None, "正当なテナントのアクセスが阻害されている"

    async def test_list_returns_only_own_tenant_data(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
        client_org_of_b: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：一覧取得で自分のテナントのデータのみ返すこと

        攻撃シナリオ：
        - 営業支援会社Bが顧客組織一覧を取得する
        - 営業支援会社Aの顧客組織が含まれていないか確認

        期待結果：
        - 自分のテナントのデータのみ返される
        """
        # Arrange
        repo = ClientOrganizationRepository(db_session)

        # 営業支援会社Aの顧客組織を作成
        client_org_a = await repo.create(
            organization_id=client_org_of_a.id,
            industry="Aの顧客",
        )

        # 営業支援会社Bの顧客組織を作成
        client_org_b = await repo.create(
            organization_id=client_org_of_b.id,
            industry="Bの顧客",
        )

        # Act: 営業支援会社Bが一覧を取得
        client_orgs_of_b = await repo.list_by_sales_support_organization(
            sales_support_org_b.id
        )

        # Assert: Bの顧客組織のみ返される
        assert len(client_orgs_of_b) == 1
        assert client_orgs_of_b[0].id == client_org_b.id
        assert client_orgs_of_b[0].industry == "Bの顧客"

        # Aの顧客組織は含まれていない
        assert all(co.id != client_org_a.id for co in client_orgs_of_b)


class TestClientContactIDORAttack:
    """顧客担当者のIDOR攻撃テスト"""

    async def test_cannot_read_other_tenant_client_contact(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客担当者を読み取れないこと
        """
        # Arrange
        org_repo = ClientOrganizationRepository(db_session)
        contact_repo = ClientContactRepository(db_session)

        # 営業支援会社Aの顧客組織と担当者を作成
        client_org_a = await org_repo.create(
            organization_id=client_org_of_a.id,
            industry="IT・情報通信",
        )
        contact_a = await contact_repo.create(
            client_organization_id=client_org_a.id,
            full_name="田中一郎",
            notes="Aの重要担当者",
        )

        # Act: 営業支援会社BがAの担当者にアクセスを試みる（IDOR攻撃）
        stolen_data = await contact_repo.find_by_id(
            contact_a.id, sales_support_org_b.id  # ← 別のテナントIDを使用
        )

        # Assert: アクセスが拒否される
        assert stolen_data is None, "🚨 IDOR脆弱性: 他のテナントの担当者データにアクセスできてしまう！"

    async def test_cannot_update_other_tenant_client_contact(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客担当者を更新できないこと
        """
        # Arrange
        org_repo = ClientOrganizationRepository(db_session)
        contact_repo = ClientContactRepository(db_session)

        client_org_a = await org_repo.create(organization_id=client_org_of_a.id)
        contact_a = await contact_repo.create(
            client_organization_id=client_org_a.id,
            full_name="田中一郎",
        )

        # Act & Assert: 営業支援会社BがAの担当者を更新しようとする
        contact_a.full_name = "悪意のある更新"
        with pytest.raises(ClientContactNotFoundError):
            await contact_repo.update(contact_a, sales_support_org_b.id)

    async def test_cannot_delete_other_tenant_client_contact(
        self,
        db_session: AsyncSession,
        sales_support_org_a: Organization,
        sales_support_org_b: Organization,
        client_org_of_a: Organization,
    ) -> None:
        """
        🚨 セキュリティテスト：他のテナントの顧客担当者を削除できないこと
        """
        # Arrange
        org_repo = ClientOrganizationRepository(db_session)
        contact_repo = ClientContactRepository(db_session)

        client_org_a = await org_repo.create(organization_id=client_org_of_a.id)
        contact_a = await contact_repo.create(
            client_organization_id=client_org_a.id,
            full_name="田中一郎",
        )

        # Act & Assert: 営業支援会社BがAの担当者を削除しようとする
        with pytest.raises(ClientContactNotFoundError):
            await contact_repo.soft_delete(contact_a.id, sales_support_org_b.id)

        # 営業支援会社Aは自分の担当者を取得できることを確認
        result = await contact_repo.find_by_id(contact_a.id, sales_support_org_a.id)
        assert result is not None, "正当なテナントのアクセスが阻害されている"
