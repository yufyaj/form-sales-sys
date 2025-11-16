"""
プロジェクトリポジトリの結合テスト

実際のデータベースを使用してProjectRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project_entity import ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.infrastructure.persistence.models import ClientOrganization, Organization
from src.infrastructure.persistence.models.organization import OrganizationType
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
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="新規プロジェクト",
            description="テスト用プロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Assert
        assert project.id > 0
        assert project.organization_id == sales_support_organization.id
        assert project.client_organization_id == client_organization.id
        assert project.name == "新規プロジェクト"
        assert project.description == "テスト用プロジェクト"
        assert project.status == ProjectStatus.PLANNING
        assert project.progress == 0
        assert project.total_lists == 0
        assert project.completed_lists == 0
        assert project.total_submissions == 0
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
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="最小プロジェクト",
        )

        # Assert
        assert project.id > 0
        assert project.name == "最小プロジェクト"
        assert project.description is None
        assert project.status == ProjectStatus.PLANNING


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
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="検索テストプロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # Act
        project = await repo.find_by_id(
            created.id, sales_support_organization.id
        )

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

    async def test_find_by_id_idor_protection(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """セキュリティ：他組織のプロジェクトは取得できない（IDOR対策）"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="組織Aのプロジェクト",
        )

        # 別の営業支援組織を作成
        other_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="other@example.com",
        )
        db_session.add(other_org)
        await db_session.flush()

        # Act - 別組織からのアクセス
        found = await repo.find_by_id(project.id, other_org.id)

        # Assert
        assert found is None  # IDOR対策により取得できない


class TestProjectRepositoryList:
    """プロジェクト一覧取得のテスト"""

    async def test_list_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：組織IDでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 3つのプロジェクトを作成
        for i in range(3):
            await repo.create(
                organization_id=sales_support_organization.id,
                client_organization_id=client_organization.id,
                name=f"プロジェクト{i+1}",
                status=ProjectStatus.ACTIVE,
            )

        # Act
        projects = await repo.list_by_organization(
            organization_id=sales_support_organization.id,
        )

        # Assert
        assert len(projects) == 3
        assert all(p.name in ["プロジェクト1", "プロジェクト2", "プロジェクト3"] for p in projects)

    async def test_list_by_organization_with_client_filter(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_base_organization: Organization,
    ) -> None:
        """正常系：顧客組織IDでフィルタできる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 2つの顧客組織を作成
        client_org1 = ClientOrganization(
            organization_id=client_base_organization.id,
            industry="製造業",
        )
        db_session.add(client_org1)
        await db_session.flush()

        # 別の顧客組織
        client_org2_base = Organization(
            name="別の顧客企業",
            type=OrganizationType.CLIENT,
            parent_organization_id=sales_support_organization.id,
        )
        db_session.add(client_org2_base)
        await db_session.flush()

        client_org2 = ClientOrganization(
            organization_id=client_org2_base.id,
            industry="小売業",
        )
        db_session.add(client_org2)
        await db_session.flush()

        # 各顧客にプロジェクトを作成
        await repo.create(
            organization_id=sales_support_organization.id,
            client_organization_id=client_org1.id,
            name="顧客1のプロジェクト",
        )
        await repo.create(
            organization_id=sales_support_organization.id,
            client_organization_id=client_org2.id,
            name="顧客2のプロジェクト",
        )

        # Act - 顧客1でフィルタ
        projects = await repo.list_by_organization(
            organization_id=sales_support_organization.id,
            client_organization_id=client_org1.id,
        )

        # Assert
        assert len(projects) == 1
        assert projects[0].name == "顧客1のプロジェクト"

    async def test_list_by_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：ステータスでフィルタできる"""
        # Arrange
        repo = ProjectRepository(db_session)

        await repo.create(
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="計画中プロジェクト",
            status=ProjectStatus.PLANNING,
        )
        await repo.create(
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="進行中プロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # Act - ACTIVEでフィルタ
        projects = await repo.list_by_organization(
            organization_id=sales_support_organization.id,
            status=ProjectStatus.ACTIVE,
        )

        # Assert
        assert len(projects) == 1
        assert projects[0].name == "進行中プロジェクト"

    async def test_list_by_organization_pagination(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：ページネーションが正しく動作する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 10件のプロジェクトを作成
        for i in range(10):
            await repo.create(
                organization_id=sales_support_organization.id,
                client_organization_id=client_organization.id,
                name=f"プロジェクト{i+1}",
            )

        # Act - 2ページ目を取得（skip=5, limit=5）
        projects = await repo.list_by_organization(
            organization_id=sales_support_organization.id,
            skip=5,
            limit=5,
        )

        # Assert
        assert len(projects) == 5


class TestProjectRepositoryCount:
    """プロジェクト数カウントのテスト"""

    async def test_count_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：組織のプロジェクト数をカウントできる"""
        # Arrange
        repo = ProjectRepository(db_session)

        for i in range(5):
            await repo.create(
                organization_id=sales_support_organization.id,
                client_organization_id=client_organization.id,
                name=f"プロジェクト{i+1}",
            )

        # Act
        count = await repo.count_by_organization(
            organization_id=sales_support_organization.id,
        )

        # Assert
        assert count == 5


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
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="更新前プロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act
        project.name = "更新後プロジェクト"
        project.status = ProjectStatus.ACTIVE
        project.description = "説明を追加"
        updated = await repo.update(project, sales_support_organization.id)

        # Assert
        assert updated.id == project.id
        assert updated.name == "更新後プロジェクト"
        assert updated.status == ProjectStatus.ACTIVE
        assert updated.description == "説明を追加"

    async def test_update_project_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないプロジェクトの更新でエラー"""
        # Arrange
        repo = ProjectRepository(db_session)
        from src.domain.entities.project_entity import ProjectEntity

        fake_entity = ProjectEntity(
            id=999999,
            organization_id=sales_support_organization.id,
            client_organization_id=1,
            name="存在しないプロジェクト",
            status=ProjectStatus.ACTIVE,
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
            organization_id=sales_support_organization.id,
            client_organization_id=client_organization.id,
            name="削除予定プロジェクト",
        )

        # Act
        await repo.soft_delete(project.id, sales_support_organization.id)

        # Assert
        deleted = await repo.find_by_id(project.id, sales_support_organization.id)
        assert deleted is None

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないプロジェクトの論理削除でエラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.soft_delete(999999, sales_support_organization.id)
