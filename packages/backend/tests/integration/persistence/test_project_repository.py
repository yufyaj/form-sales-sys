"""
プロジェクトリポジトリの統合テスト

実際のデータベースを使用してリポジトリ操作をテストします。
"""
from datetime import date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project_entity import ProjectPriority, ProjectStatus
from src.domain.exceptions import (
    ClientOrganizationNotFoundError,
    InvalidBudgetError,
    InvalidDateRangeError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from src.infrastructure.persistence.models.client_organization import (
    ClientOrganization,
)
from src.infrastructure.persistence.models.organization import Organization, OrganizationType
from src.infrastructure.persistence.models.user import User
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
    from src.infrastructure.persistence.repositories.client_organization_repository import (
        ClientOrganizationRepository,
    )

    repo = ClientOrganizationRepository(db_session)
    client_org = await repo.create(
        organization_id=client_base_organization.id,
        industry="IT・情報通信",
        employee_count=500,
    )
    return client_org


@pytest.fixture
async def admin_user(
    db_session: AsyncSession, sales_support_organization: Organization
) -> User:
    """テスト用管理者ユーザーを作成"""
    user = User(
        organization_id=sales_support_organization.id,
        email="admin@example.com",
        full_name="管理者",
        hashed_password="hashed_password",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.mark.asyncio
class TestProjectRepository:
    """ProjectRepositoryの統合テストクラス"""

    async def test_create_project_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """プロジェクト作成が成功する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="新規Webサイト構築",
            status=ProjectStatus.PLANNING,
            description="コーポレートサイトのリニューアル",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            estimated_budget=5000000,
            actual_budget=None,
            priority=ProjectPriority.HIGH.value,
            notes="Q1完了目標",
        )

        # Assert
        assert project.id is not None
        assert project.client_organization_id == client_organization.id
        assert project.name == "新規Webサイト構築"
        assert project.status == ProjectStatus.PLANNING
        assert project.description == "コーポレートサイトのリニューアル"
        assert project.start_date == date(2025, 1, 1)
        assert project.end_date == date(2025, 3, 31)
        assert project.estimated_budget == 5000000
        assert project.actual_budget is None
        assert project.priority == ProjectPriority.HIGH
        assert project.notes == "Q1完了目標"
        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.deleted_at is None

    async def test_create_project_with_owner_user_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
        admin_user: User,
    ) -> None:
        """owner_user_idを指定してプロジェクト作成が成功する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="新規プロジェクト",
            status=ProjectStatus.PLANNING,
            owner_user_id=admin_user.id,
        )

        # Assert
        assert project.id is not None
        assert project.owner_user_id == admin_user.id

    async def test_create_project_fails_when_client_organization_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """存在しない顧客組織IDでプロジェクト作成が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)
        non_existent_id = 99999

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.create(
                client_organization_id=non_existent_id,
                requesting_organization_id=sales_support_organization.id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
            )

    async def test_create_project_fails_when_client_organization_belongs_to_different_org(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """別組織の顧客組織に対してプロジェクト作成が失敗する（IDOR対策）"""
        # Arrange
        repo = ProjectRepository(db_session)
        different_org_id = 99999

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=different_org_id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
            )

    async def test_create_project_fails_when_owner_user_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """存在しないowner_user_idでプロジェクト作成が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)
        non_existent_user_id = 99999

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
                owner_user_id=non_existent_user_id,
            )

    async def test_create_project_fails_when_date_range_invalid(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """開始日が終了日より後の場合、プロジェクト作成が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidDateRangeError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
                start_date=date(2025, 3, 31),
                end_date=date(2025, 1, 1),
            )

    async def test_create_project_fails_when_estimated_budget_negative(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """見積予算が負の値の場合、プロジェクト作成が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidBudgetError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
                estimated_budget=-1000,
            )

    async def test_create_project_fails_when_actual_budget_negative(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """実績予算が負の値の場合、プロジェクト作成が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidBudgetError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="テストプロジェクト",
                status=ProjectStatus.PLANNING,
                actual_budget=-1000,
            )

    async def test_find_by_id_returns_project_when_exists(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """プロジェクトが存在する場合、find_by_idはプロジェクトを返す"""
        # Arrange
        repo = ProjectRepository(db_session)
        created_project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act
        found_project = await repo.find_by_id(
            project_id=created_project.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert found_project is not None
        assert found_project.id == created_project.id
        assert found_project.name == "テストプロジェクト"

    async def test_find_by_id_returns_none_when_not_exists(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """プロジェクトが存在しない場合、find_by_idはNoneを返す"""
        # Arrange
        repo = ProjectRepository(db_session)
        non_existent_id = 99999

        # Act
        found_project = await repo.find_by_id(
            project_id=non_existent_id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert found_project is None

    async def test_find_by_id_returns_none_when_different_organization(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """別組織のプロジェクトを検索した場合、find_by_idはNoneを返す（IDOR対策）"""
        # Arrange
        repo = ProjectRepository(db_session)
        created_project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )
        different_org_id = 99999

        # Act
        found_project = await repo.find_by_id(
            project_id=created_project.id,
            requesting_organization_id=different_org_id,
        )

        # Assert
        assert found_project is None

    async def test_list_by_client_organization_returns_projects(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """顧客組織に属するプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト1",
            status=ProjectStatus.PLANNING,
        )
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト2",
            status=ProjectStatus.IN_PROGRESS,
        )

        # Act
        projects = await repo.list_by_client_organization(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert len(projects) == 2
        assert projects[0].name in ["プロジェクト1", "プロジェクト2"]
        assert projects[1].name in ["プロジェクト1", "プロジェクト2"]

    async def test_list_by_client_organization_with_pagination(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """ページネーション付きでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        for i in range(5):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name=f"プロジェクト{i + 1}",
                status=ProjectStatus.PLANNING,
            )

        # Act
        projects = await repo.list_by_client_organization(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            skip=2,
            limit=2,
        )

        # Assert
        assert len(projects) == 2

    async def test_list_by_sales_support_organization_returns_all_projects(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """営業支援会社に属する全顧客のプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト1",
            status=ProjectStatus.PLANNING,
        )
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト2",
            status=ProjectStatus.IN_PROGRESS,
        )

        # Act
        projects = await repo.list_by_sales_support_organization(
            sales_support_organization_id=sales_support_organization.id,
        )

        # Assert
        assert len(projects) == 2

    async def test_list_by_sales_support_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """ステータスフィルタ付きでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト1",
            status=ProjectStatus.PLANNING,
        )
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="プロジェクト2",
            status=ProjectStatus.IN_PROGRESS,
        )

        # Act
        projects = await repo.list_by_sales_support_organization(
            sales_support_organization_id=sales_support_organization.id,
            status_filter=ProjectStatus.IN_PROGRESS,
        )

        # Assert
        assert len(projects) == 1
        assert projects[0].name == "プロジェクト2"
        assert projects[0].status == ProjectStatus.IN_PROGRESS

    async def test_update_project_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """プロジェクト更新が成功する"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="旧プロジェクト名",
            status=ProjectStatus.PLANNING,
        )

        # Act
        project.name = "新プロジェクト名"
        project.status = ProjectStatus.IN_PROGRESS
        project.description = "更新された説明"
        updated_project = await repo.update(
            project=project,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert updated_project.id == project.id
        assert updated_project.name == "新プロジェクト名"
        assert updated_project.status == ProjectStatus.IN_PROGRESS
        assert updated_project.description == "更新された説明"

    async def test_update_project_fails_when_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """存在しないプロジェクトの更新が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )
        project.id = 99999  # 存在しないID

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.update(
                project=project,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_update_project_fails_when_invalid_date_range(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """不正な日付範囲でプロジェクト更新が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act
        project.start_date = date(2025, 3, 31)
        project.end_date = date(2025, 1, 1)

        # Assert
        with pytest.raises(InvalidDateRangeError):
            await repo.update(
                project=project,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_soft_delete_project_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """プロジェクトの論理削除が成功する"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act
        await repo.soft_delete(
            project_id=project.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        found_project = await repo.find_by_id(
            project_id=project.id,
            requesting_organization_id=sales_support_organization.id,
        )
        assert found_project is None  # 論理削除されたプロジェクトは取得できない

    async def test_soft_delete_project_fails_when_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """存在しないプロジェクトの論理削除が失敗する"""
        # Arrange
        repo = ProjectRepository(db_session)
        non_existent_id = 99999

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.soft_delete(
                project_id=non_existent_id,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_soft_delete_project_fails_when_different_organization(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """別組織のプロジェクトの論理削除が失敗する（IDOR対策）"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )
        different_org_id = 99999

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await repo.soft_delete(
                project_id=project.id,
                requesting_organization_id=different_org_id,
            )
