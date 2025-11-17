"""
プロジェクトユースケースのユニットテスト

モックを使用してビジネスロジックをテストします。
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectPriorityEnum,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.application.use_cases.project_use_cases import ProjectUseCases
from src.domain.entities.project_entity import (
    ProjectEntity,
    ProjectPriority,
    ProjectStatus,
)
from src.domain.exceptions import ProjectNotFoundError


@pytest.fixture
def mock_project_repository() -> AsyncMock:
    """プロジェクトリポジトリのモックを作成"""
    return AsyncMock()


@pytest.fixture
def project_use_cases(mock_project_repository: AsyncMock) -> ProjectUseCases:
    """プロジェクトユースケースのインスタンスを作成"""
    return ProjectUseCases(project_repository=mock_project_repository)


class TestProjectUseCases:
    """ProjectUseCasesのテストクラス"""

    @pytest.mark.asyncio
    async def test_create_project_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクト作成が成功する"""
        # Arrange
        request = ProjectCreateRequest(
            client_organization_id=10,
            name="新規Webサイト構築",
            description="コーポレートサイトのリニューアル",
            status=ProjectStatusEnum.PLANNING,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            estimated_budget=5000000,
            priority=ProjectPriorityEnum.HIGH,
            notes="Q1完了目標",
        )

        expected_entity = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="新規Webサイト構築",
            description="コーポレートサイトのリニューアル",
            status=ProjectStatus.PLANNING,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            estimated_budget=5000000,
            priority=ProjectPriority.HIGH,
            notes="Q1完了目標",
        )

        mock_project_repository.create.return_value = expected_entity

        # Act
        result = await project_use_cases.create_project(
            requesting_organization_id=1,
            request=request,
        )

        # Assert
        assert result == expected_entity
        mock_project_repository.create.assert_called_once()
        call_kwargs = mock_project_repository.create.call_args.kwargs
        assert call_kwargs["client_organization_id"] == 10
        assert call_kwargs["requesting_organization_id"] == 1
        assert call_kwargs["name"] == "新規Webサイト構築"
        assert call_kwargs["status"] == ProjectStatus.PLANNING

    @pytest.mark.asyncio
    async def test_get_project_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクト取得が成功する"""
        # Arrange
        expected_entity = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        mock_project_repository.find_by_id.return_value = expected_entity

        # Act
        result = await project_use_cases.get_project(
            project_id=1,
            requesting_organization_id=1,
        )

        # Assert
        assert result == expected_entity
        mock_project_repository.find_by_id.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )

    @pytest.mark.asyncio
    async def test_get_project_raises_not_found_error(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクトが見つからない場合、get_projectは例外を発生させる"""
        # Arrange
        mock_project_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await project_use_cases.get_project(
                project_id=1,
                requesting_organization_id=1,
            )

    @pytest.mark.asyncio
    async def test_list_projects_by_client_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """顧客別プロジェクト一覧取得が成功する"""
        # Arrange
        expected_entities = [
            ProjectEntity(
                id=1,
                client_organization_id=10,
                name="プロジェクト1",
                status=ProjectStatus.PLANNING,
            ),
            ProjectEntity(
                id=2,
                client_organization_id=10,
                name="プロジェクト2",
                status=ProjectStatus.IN_PROGRESS,
            ),
        ]

        mock_project_repository.list_by_client_organization.return_value = (
            expected_entities
        )

        # Act
        projects, total = await project_use_cases.list_projects_by_client(
            client_organization_id=10,
            requesting_organization_id=1,
            page=1,
            page_size=20,
        )

        # Assert
        assert projects == expected_entities
        assert total == 2
        mock_project_repository.list_by_client_organization.assert_called_once_with(
            client_organization_id=10,
            requesting_organization_id=1,
            skip=0,
            limit=20,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_projects_by_client_with_pagination(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """ページネーション付きで顧客別プロジェクト一覧取得が成功する"""
        # Arrange
        mock_project_repository.list_by_client_organization.return_value = []

        # Act
        await project_use_cases.list_projects_by_client(
            client_organization_id=10,
            requesting_organization_id=1,
            page=3,
            page_size=50,
        )

        # Assert
        mock_project_repository.list_by_client_organization.assert_called_once_with(
            client_organization_id=10,
            requesting_organization_id=1,
            skip=100,  # (3 - 1) * 50
            limit=50,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_projects_by_client_limits_page_size_to_100(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """ページサイズが100を超える場合、100に制限される"""
        # Arrange
        mock_project_repository.list_by_client_organization.return_value = []

        # Act
        await project_use_cases.list_projects_by_client(
            client_organization_id=10,
            requesting_organization_id=1,
            page=1,
            page_size=200,
        )

        # Assert
        call_kwargs = (
            mock_project_repository.list_by_client_organization.call_args.kwargs
        )
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_list_projects_by_sales_support_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """営業支援会社別プロジェクト一覧取得が成功する"""
        # Arrange
        expected_entities = [
            ProjectEntity(
                id=1,
                client_organization_id=10,
                name="プロジェクト1",
                status=ProjectStatus.PLANNING,
            ),
            ProjectEntity(
                id=2,
                client_organization_id=11,
                name="プロジェクト2",
                status=ProjectStatus.IN_PROGRESS,
            ),
        ]

        mock_project_repository.list_by_sales_support_organization.return_value = (
            expected_entities
        )

        # Act
        projects, total = await project_use_cases.list_projects_by_sales_support(
            sales_support_organization_id=1,
            status=None,
            page=1,
            page_size=20,
        )

        # Assert
        assert projects == expected_entities
        assert total == 2
        mock_project_repository.list_by_sales_support_organization.assert_called_once_with(
            sales_support_organization_id=1,
            skip=0,
            limit=20,
            status_filter=None,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_projects_by_sales_support_with_status_filter(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """ステータスフィルタ付きで営業支援会社別プロジェクト一覧取得が成功する"""
        # Arrange
        mock_project_repository.list_by_sales_support_organization.return_value = []

        # Act
        await project_use_cases.list_projects_by_sales_support(
            sales_support_organization_id=1,
            status=ProjectStatusEnum.IN_PROGRESS,
            page=1,
            page_size=20,
        )

        # Assert
        call_kwargs = (
            mock_project_repository.list_by_sales_support_organization.call_args.kwargs
        )
        assert call_kwargs["status_filter"] == ProjectStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_update_project_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクト更新が成功する"""
        # Arrange
        existing_project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="旧プロジェクト名",
            status=ProjectStatus.PLANNING,
        )

        updated_project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="新プロジェクト名",
            status=ProjectStatus.IN_PROGRESS,
            description="更新された説明",
        )

        mock_project_repository.find_by_id.return_value = existing_project
        mock_project_repository.update.return_value = updated_project

        request = ProjectUpdateRequest(
            name="新プロジェクト名",
            status=ProjectStatusEnum.IN_PROGRESS,
            description="更新された説明",
        )

        # Act
        result = await project_use_cases.update_project(
            project_id=1,
            requesting_organization_id=1,
            request=request,
        )

        # Assert
        assert result == updated_project
        mock_project_repository.find_by_id.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )
        mock_project_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_project_raises_not_found_error(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクトが見つからない場合、update_projectは例外を発生させる"""
        # Arrange
        mock_project_repository.find_by_id.return_value = None

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await project_use_cases.update_project(
                project_id=1,
                requesting_organization_id=1,
                request=request,
            )

    @pytest.mark.asyncio
    async def test_update_project_updates_only_specified_fields(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """指定されたフィールドのみ更新される"""
        # Arrange
        existing_project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="旧プロジェクト名",
            status=ProjectStatus.PLANNING,
            description="旧説明",
        )

        mock_project_repository.find_by_id.return_value = existing_project
        mock_project_repository.update.return_value = existing_project

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act
        await project_use_cases.update_project(
            project_id=1,
            requesting_organization_id=1,
            request=request,
        )

        # Assert
        update_call_args = mock_project_repository.update.call_args.kwargs
        updated_entity = update_call_args["project"]
        assert updated_entity.name == "新プロジェクト名"
        assert updated_entity.status == ProjectStatus.PLANNING  # 変更されない
        assert updated_entity.description == "旧説明"  # 変更されない

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクト削除が成功する"""
        # Arrange
        existing_project = ProjectEntity(
            id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.PLANNING,
        )

        mock_project_repository.find_by_id.return_value = existing_project

        # Act
        await project_use_cases.delete_project(
            project_id=1,
            requesting_organization_id=1,
        )

        # Assert
        mock_project_repository.find_by_id.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )
        mock_project_repository.soft_delete.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )

    @pytest.mark.asyncio
    async def test_delete_project_raises_not_found_error(
        self,
        project_use_cases: ProjectUseCases,
        mock_project_repository: AsyncMock,
    ) -> None:
        """プロジェクトが見つからない場合、delete_projectは例外を発生させる"""
        # Arrange
        mock_project_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await project_use_cases.delete_project(
                project_id=1,
                requesting_organization_id=1,
            )
