"""
プロジェクトリポジトリの結合テスト

実際のデータベースを使用してProjectRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
from datetime import date

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
from src.infrastructure.persistence.models import ClientOrganization, Organization, User
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


@pytest.fixture
async def test_user(
    db_session: AsyncSession, sales_support_organization: Organization
) -> User:
    """テスト用ユーザーを作成"""
    user = User(
        email="testuser@example.com",
        hashed_password="dummy_hash",
        full_name="テストユーザー",
        organization_id=sales_support_organization.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


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
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="新規Webサイト構築",
            status=ProjectStatus.PLANNING,
            description="コーポレートサイトのリニューアル",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            estimated_budget=5000000,
            priority=ProjectPriority.HIGH.value,
            notes="Q1完了目標",
        )

        # Assert
        assert project.id > 0
        assert project.client_organization_id == client_organization.id
        assert project.name == "新規Webサイト構築"
        assert project.status == ProjectStatus.PLANNING
        assert project.description == "コーポレートサイトのリニューアル"
        assert project.start_date == date(2025, 1, 1)
        assert project.end_date == date(2025, 3, 31)
        assert project.estimated_budget == 5000000
        assert project.priority == ProjectPriority.HIGH
        assert project.notes == "Q1完了目標"

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
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="最小プロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Assert
        assert project.id > 0
        assert project.client_organization_id == client_organization.id
        assert project.name == "最小プロジェクト"
        assert project.status == ProjectStatus.PLANNING
        assert project.description is None
        assert project.start_date is None
        assert project.end_date is None

    async def test_create_project_with_owner(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
        test_user: User,
    ) -> None:
        """正常系：プロジェクトオーナーを指定してプロジェクトを作成できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="オーナー付きプロジェクト",
            status=ProjectStatus.PLANNING,
            owner_user_id=test_user.id,
        )

        # Assert
        assert project.id > 0
        assert project.owner_user_id == test_user.id

    async def test_create_project_invalid_client_organization(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しない顧客組織IDでエラー（IDOR脆弱性対策）"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.create(
                client_organization_id=999999,
                requesting_organization_id=sales_support_organization.id,
                name="不正なプロジェクト",
                status=ProjectStatus.PLANNING,
            )

    async def test_create_project_different_tenant_client_organization(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """セキュリティ：別テナントの顧客組織IDでプロジェクト作成できない（IDOR脆弱性対策）"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 別の営業支援会社を作成
        other_sales_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="other@example.com",
        )
        db_session.add(other_sales_org)
        await db_session.flush()

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=other_sales_org.id,
                name="不正なプロジェクト",
                status=ProjectStatus.PLANNING,
            )

    async def test_create_project_invalid_owner_user(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：存在しないユーザーIDでエラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="不正なオーナー付きプロジェクト",
                status=ProjectStatus.PLANNING,
                owner_user_id=999999,
            )

    async def test_create_project_different_tenant_owner_user(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """セキュリティ：別テナントのユーザーIDでプロジェクト作成できない（IDOR脆弱性対策）"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 別の営業支援会社とそのユーザーを作成
        other_sales_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="other@example.com",
        )
        db_session.add(other_sales_org)
        await db_session.flush()

        other_user = User(
            email="otheruser@example.com",
            hashed_password="dummy_hash",
            full_name="別のユーザー",
            organization_id=other_sales_org.id,
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.flush()

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="不正なオーナー付きプロジェクト",
                status=ProjectStatus.PLANNING,
                owner_user_id=other_user.id,
            )


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
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="テストプロジェクト",
            status=ProjectStatus.IN_PROGRESS,
            estimated_budget=3000000,
        )

        # Act
        project = await repo.find_by_id(created.id, sales_support_organization.id)

        # Assert
        assert project is not None
        assert project.id == created.id
        assert project.name == "テストプロジェクト"
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.estimated_budget == 3000000

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

    async def test_find_by_id_multi_tenant_isolation(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """セキュリティ：別の営業支援会社のプロジェクトは取得できない（マルチテナント分離）"""
        # Arrange
        repo = ProjectRepository(db_session)
        created = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="極秘プロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # 別の営業支援会社を作成
        other_sales_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="other@example.com",
        )
        db_session.add(other_sales_org)
        await db_session.flush()

        # Act
        project = await repo.find_by_id(created.id, other_sales_org.id)

        # Assert - IDOR脆弱性対策により、別テナントのプロジェクトは取得できない
        assert project is None


class TestProjectRepositoryList:
    """プロジェクト一覧取得のテスト"""

    async def test_list_by_client_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：顧客組織IDでプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 3つのプロジェクトを作成
        for i in range(3):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name=f"プロジェクト{i+1}",
                status=ProjectStatus.PLANNING,
            )

        # Act
        projects = await repo.list_by_client_organization(
            client_organization.id, sales_support_organization.id
        )

        # Assert
        assert len(projects) == 3
        assert all(
            p.name in ["プロジェクト1", "プロジェクト2", "プロジェクト3"]
            for p in projects
        )

    async def test_list_by_sales_support_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：営業支援会社IDで全顧客のプロジェクト一覧を取得できる"""
        # Arrange
        repo = ProjectRepository(db_session)

        # 2つの顧客組織を作成
        for i in range(2):
            client_org = Organization(
                name=f"顧客企業{i+1}",
                type=OrganizationType.CLIENT,
                parent_organization_id=sales_support_organization.id,
            )
            db_session.add(client_org)
            await db_session.flush()

            client_organization = ClientOrganization(
                organization_id=client_org.id,
                industry=f"業種{i+1}",
            )
            db_session.add(client_organization)
            await db_session.flush()

            # 各顧客に2つのプロジェクト
            for j in range(2):
                await repo.create(
                    client_organization_id=client_organization.id,
                    requesting_organization_id=sales_support_organization.id,
                    name=f"顧客{i+1}のプロジェクト{j+1}",
                    status=ProjectStatus.IN_PROGRESS,
                )

        # Act
        projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id
        )

        # Assert
        assert len(projects) == 4

    async def test_list_by_sales_support_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """正常系：ステータスフィルタでプロジェクトを絞り込める"""
        # Arrange
        repo = ProjectRepository(db_session)

        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="企画中プロジェクト",
            status=ProjectStatus.PLANNING,
        )
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="進行中プロジェクト",
            status=ProjectStatus.IN_PROGRESS,
        )
        await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="完了プロジェクト",
            status=ProjectStatus.COMPLETED,
        )

        # Act
        planning_projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id,
            status_filter=ProjectStatus.PLANNING,
        )
        in_progress_projects = await repo.list_by_sales_support_organization(
            sales_support_organization.id,
            status_filter=ProjectStatus.IN_PROGRESS,
        )

        # Assert
        assert len(planning_projects) == 1
        assert planning_projects[0].status == ProjectStatus.PLANNING
        assert len(in_progress_projects) == 1
        assert in_progress_projects[0].status == ProjectStatus.IN_PROGRESS


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
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="旧プロジェクト名",
            status=ProjectStatus.PLANNING,
            estimated_budget=1000000,
        )

        # Act
        project.name = "新プロジェクト名"
        project.status = ProjectStatus.IN_PROGRESS
        project.estimated_budget = 2000000
        project.actual_budget = 1500000
        project.notes = "予算増額済み"
        updated = await repo.update(project, sales_support_organization.id)

        # Assert
        assert updated.id == project.id
        assert updated.name == "新プロジェクト名"
        assert updated.status == ProjectStatus.IN_PROGRESS
        assert updated.estimated_budget == 2000000
        assert updated.actual_budget == 1500000
        assert updated.notes == "予算増額済み"

    async def test_update_project_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないプロジェクトの更新でエラー"""
        # Arrange
        repo = ProjectRepository(db_session)
        from src.domain.entities.project_entity import ProjectEntity

        fake_entity = ProjectEntity(
            id=999999,
            client_organization_id=1,
            name="存在しない",
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
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="削除予定プロジェクト",
            status=ProjectStatus.CANCELLED,
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


class TestProjectRepositoryValidation:
    """プロジェクトバリデーションのテスト"""

    async def test_create_project_invalid_date_range(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：開始日が終了日より後の場合エラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidDateRangeError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="不正な日付範囲プロジェクト",
                status=ProjectStatus.PLANNING,
                start_date=date(2025, 12, 31),
                end_date=date(2025, 1, 1),
            )

    async def test_create_project_negative_estimated_budget(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：見積予算が負の値の場合エラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidBudgetError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="負の見積予算プロジェクト",
                status=ProjectStatus.PLANNING,
                estimated_budget=-1000000,
            )

    async def test_create_project_negative_actual_budget(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：実績予算が負の値の場合エラー"""
        # Arrange
        repo = ProjectRepository(db_session)

        # Act & Assert
        with pytest.raises(InvalidBudgetError):
            await repo.create(
                client_organization_id=client_organization.id,
                requesting_organization_id=sales_support_organization.id,
                name="負の実績予算プロジェクト",
                status=ProjectStatus.PLANNING,
                actual_budget=-500000,
            )

    async def test_update_project_invalid_date_range(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：更新時に開始日が終了日より後の場合エラー"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="日付テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        # Act & Assert
        project.start_date = date(2025, 12, 31)
        project.end_date = date(2025, 1, 1)
        with pytest.raises(InvalidDateRangeError):
            await repo.update(project, sales_support_organization.id)

    async def test_update_project_negative_budget(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        client_organization: ClientOrganization,
    ) -> None:
        """異常系：更新時に予算が負の値の場合エラー"""
        # Arrange
        repo = ProjectRepository(db_session)
        project = await repo.create(
            client_organization_id=client_organization.id,
            requesting_organization_id=sales_support_organization.id,
            name="予算テストプロジェクト",
            status=ProjectStatus.PLANNING,
            estimated_budget=1000000,
        )

        # Act & Assert
        project.estimated_budget = -1000000
        with pytest.raises(InvalidBudgetError):
            await repo.update(project, sales_support_organization.id)
