"""
プロジェクトリポジトリの結合テスト

実際のデータベースを使用してProjectRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project_entity import ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.client_organization import ClientOrganization
from src.infrastructure.persistence.repositories.project_repository import (
    ProjectRepository,
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
async def client_organization(
    db_session: AsyncSession, client_base_organization: Organization
) -> ClientOrganization:
    """テスト用顧客組織を作成"""
    client_org = ClientOrganization(
        organization_id=client_base_organization.id,
        industry="IT・情報通信",
        employee_count=500,
    )
    db_session.add(client_org)
    await db_session.flush()
    return client_org


class TestProjectRepositoryCreate:
    """プロジェクト作成のテスト"""

    async def test_create_project_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：プロジェクトを作成できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.create(
            name="新規Webサイト構築プロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 4, 1),
            end_date=date(2025, 9, 30),
            description="新しいコーポレートサイトの構築",
        )

        # Assert
        assert project.id > 0
        assert project.name == "新規Webサイト構築プロジェクト"
        assert project.client_organization_id == client_organization.id
        assert project.sales_support_organization_id == sales_support_organization.id
        assert project.status == ProjectStatus.PLANNING
        assert project.start_date == date(2025, 4, 1)
        assert project.end_date == date(2025, 9, 30)
        assert project.description == "新しいコーポレートサイトの構築"
        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.deleted_at is None

    async def test_create_project_minimal(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：必須項目のみでプロジェクトを作成できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.create(
            name="最小プロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
        )

        # Assert
        assert project.id > 0
        assert project.name == "最小プロジェクト"
        assert project.status == ProjectStatus.PLANNING  # デフォルト
        assert project.start_date is None
        assert project.end_date is None
        assert project.description is None


class TestProjectRepositoryFind:
    """プロジェクト検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：IDでプロジェクトを検索できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        created = await repo.create(
            name="検索テストプロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.ACTIVE,
        )

        # Act
        project = await repo.find_by_id(created.id, sales_support_organization.id)

        # Assert
        assert project is not None
        assert project.id == created.id
        assert project.name == "検索テストプロジェクト"
        assert project.status == ProjectStatus.ACTIVE

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.find_by_id(999999, sales_support_organization.id)

        # Assert
        assert project is None

    async def test_find_by_id_different_organization(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """セキュリティ：異なる営業支援会社のプロジェクトは取得できない（IDOR対策）"""
        # Arrange
        repo = ProjectRepository(db_session)
        created = await repo.create(
            name="IDOR対策テスト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
        )

        # 別の営業支援会社を作成
        other_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="other@example.com",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Act
        project = await repo.find_by_id(created.id, other_org.id)

        # Assert
        assert project is None  # テナント分離により取得できない

    async def test_list_by_sales_support_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：営業支援会社IDでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 3つのプロジェクトを作成
        for i in range(3):
            await repo.create(
                name=f"プロジェクト{i+1}",
                client_organization_id=client_organization.id,
                sales_support_organization_id=sales_support_organization.id,
                status=ProjectStatus.ACTIVE if i % 2 == 0 else ProjectStatus.PLANNING,
            )

        # Act
        projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id
        )

        # Assert
        assert len(projects) == 3
        assert all(p.name in ["プロジェクト1", "プロジェクト2", "プロジェクト3"] for p in projects)

    async def test_list_by_sales_support_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：ステータスでフィルタリングして一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 異なるステータスのプロジェクトを作成
        await repo.create(
            name="進行中プロジェクト1",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.ACTIVE,
        )
        await repo.create(
            name="進行中プロジェクト2",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.ACTIVE,
        )
        await repo.create(
            name="企画中プロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.PLANNING,
        )

        # Act
        active_projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id, status=ProjectStatus.ACTIVE
        )

        # Assert
        assert len(active_projects) == 2
        assert all(p.status == ProjectStatus.ACTIVE for p in active_projects)

    async def test_list_by_client_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：顧客組織IDでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 2つのプロジェクトを作成
        for i in range(2):
            await repo.create(
                name=f"顧客プロジェクト{i+1}",
                client_organization_id=client_organization.id,
                sales_support_organization_id=sales_support_organization.id,
            )

        # Act
        projects = await repo.list_by_client_organization(
            client_organization.id, sales_support_organization.id
        )

        # Assert
        assert len(projects) == 2
        assert all(p.client_organization_id == client_organization.id for p in projects)


class TestProjectRepositoryUpdate:
    """プロジェクト更新のテスト"""

    async def test_update_project_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：プロジェクトを更新できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            name="更新前プロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.PLANNING,
        )

        # Act
        project.name = "更新後プロジェクト"
        project.status = ProjectStatus.ACTIVE
        project.description = "更新されました"
        updated = await repo.update(project, sales_support_organization.id)

        # Assert
        assert updated.id == project.id
        assert updated.name == "更新後プロジェクト"
        assert updated.status == ProjectStatus.ACTIVE
        assert updated.description == "更新されました"

    async def test_update_project_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないプロジェクトの更新でエラー"""
        # Arrange
        repo = ProjectRepository(db_session)
        from src.domain.entities.project_entity import ProjectEntity

        fake_entity = ProjectEntity(
            id=999999,
            name="存在しないプロジェクト",
            client_organization_id=1,
            sales_support_organization_id=sales_support_organization.id,
            status=ProjectStatus.PLANNING,
        )

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.update(fake_entity, sales_support_organization.id)


class TestProjectRepositorySoftDelete:
    """プロジェクト論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：プロジェクトを論理削除できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            name="削除予定プロジェクト",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
        )

        # Act
        await repo.soft_delete(project.id, sales_support_organization.id)

        # Assert
        deleted = await repo.find_by_id(project.id, sales_support_organization.id)
        assert deleted is None  # 論理削除されたプロジェクトは検索結果に含まれない

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないプロジェクトの論理削除でエラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.soft_delete(999999, sales_support_organization.id)

    async def test_soft_deleted_projects_excluded_from_list(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：論理削除されたプロジェクトは一覧に含まれない"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 2つのプロジェクトを作成
        project1 = await repo.create(
            name="プロジェクト1",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
        )
        await repo.create(
            name="プロジェクト2",
            client_organization_id=client_organization.id,
            sales_support_organization_id=sales_support_organization.id,
        )

        # 1つを削除
        await repo.soft_delete(project1.id, sales_support_organization.id)

        # Act
        projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id
        )

        # Assert
        assert len(projects) == 1
        assert projects[0].name == "プロジェクト2"
