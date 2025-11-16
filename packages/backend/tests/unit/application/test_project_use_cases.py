"""
プロジェクトユースケースの単体テスト

モックを使用してユースケースのビジネスロジックを検証します。
リポジトリはモックで代替し、ビジネスロジックのみをテストします。
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.application.use_cases.project_use_cases import ProjectUseCases
from src.domain.entities.client_organization_entity import ClientOrganizationEntity
from src.domain.entities.project_entity import ProjectEntity, ProjectStatus
from src.domain.exceptions import (
    ClientOrganizationNotFoundError,
    ProjectCannotBeEditedError,
    ProjectNotFoundError,
    ProjectValidationError,
)


class TestProjectUseCasesCreate:
    """プロジェクト作成ユースケースのテスト"""

    async def test_create_project_success(self) -> None:
        """正常系：プロジェクトを作成できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_client_org = Mock(spec=ClientOrganizationEntity)
        mock_client_org.id = 10
        mock_client_org_repo.find_by_id = AsyncMock(return_value=mock_client_org)

        mock_project = Mock(spec=ProjectEntity)
        mock_project.id = 1
        mock_project.name = "新規プロジェクト"
        mock_project.organization_id = 1
        mock_project.client_organization_id = 10
        mock_project_repo.create = AsyncMock(return_value=mock_project)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectCreateRequest(
            name="新規プロジェクト",
            description="テスト用プロジェクト",
            client_organization_id=10,
            status=ProjectStatusEnum.PLANNING,
        )

        # Act
        project = await use_case.create_project(
            organization_id=1,
            request=request,
        )

        # Assert
        assert project.id == 1
        assert project.name == "新規プロジェクト"
        mock_client_org_repo.find_by_id.assert_called_once_with(
            client_organization_id=10,
            requesting_organization_id=1,
        )
        mock_project_repo.create.assert_called_once()

    async def test_create_project_client_organization_not_found(self) -> None:
        """異常系：顧客組織が見つからない場合、エラー"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()
        mock_client_org_repo.find_by_id = AsyncMock(return_value=None)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectCreateRequest(
            name="新規プロジェクト",
            client_organization_id=999,
        )

        # Act & Assert
        with pytest.raises(ClientOrganizationNotFoundError):
            await use_case.create_project(
                organization_id=1,
                request=request,
            )


class TestProjectUseCasesGet:
    """プロジェクト取得ユースケースのテスト"""

    async def test_get_project_success(self) -> None:
        """正常系：プロジェクトを取得できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_project = Mock(spec=ProjectEntity)
        mock_project.id = 1
        mock_project.name = "テストプロジェクト"
        mock_project_repo.find_by_id = AsyncMock(return_value=mock_project)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        project = await use_case.get_project(
            project_id=1,
            organization_id=1,
        )

        # Assert
        assert project.id == 1
        assert project.name == "テストプロジェクト"
        mock_project_repo.find_by_id.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )

    async def test_get_project_not_found(self) -> None:
        """異常系：プロジェクトが見つからない場合、エラー"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()
        mock_project_repo.find_by_id = AsyncMock(return_value=None)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await use_case.get_project(
                project_id=999,
                organization_id=1,
            )


class TestProjectUseCasesList:
    """プロジェクト一覧取得ユースケースのテスト"""

    async def test_list_projects_success(self) -> None:
        """正常系：プロジェクト一覧を取得できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_projects = [
            Mock(spec=ProjectEntity, id=1, name="プロジェクト1"),
            Mock(spec=ProjectEntity, id=2, name="プロジェクト2"),
        ]
        mock_project_repo.list_by_organization = AsyncMock(return_value=mock_projects)
        mock_project_repo.count_by_organization = AsyncMock(return_value=2)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        projects, total = await use_case.list_projects(
            organization_id=1,
            page=1,
            page_size=20,
        )

        # Assert
        assert len(projects) == 2
        assert total == 2
        assert projects[0].name == "プロジェクト1"
        mock_project_repo.list_by_organization.assert_called_once_with(
            organization_id=1,
            client_organization_id=None,
            status=None,
            skip=0,
            limit=20,
            include_deleted=False,
        )

    async def test_list_projects_with_client_filter(self) -> None:
        """正常系：顧客フィルタを適用してプロジェクト一覧を取得できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_projects = [Mock(spec=ProjectEntity, id=1, name="プロジェクト1")]
        mock_project_repo.list_by_organization = AsyncMock(return_value=mock_projects)
        mock_project_repo.count_by_organization = AsyncMock(return_value=1)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        projects, total = await use_case.list_projects(
            organization_id=1,
            client_organization_id=10,
            page=1,
            page_size=20,
        )

        # Assert
        assert len(projects) == 1
        assert total == 1
        mock_project_repo.list_by_organization.assert_called_once_with(
            organization_id=1,
            client_organization_id=10,
            status=None,
            skip=0,
            limit=20,
            include_deleted=False,
        )

    async def test_list_projects_with_status_filter(self) -> None:
        """正常系：ステータスフィルタを適用してプロジェクト一覧を取得できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_projects = [Mock(spec=ProjectEntity, id=1, name="プロジェクト1")]
        mock_project_repo.list_by_organization = AsyncMock(return_value=mock_projects)
        mock_project_repo.count_by_organization = AsyncMock(return_value=1)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        projects, total = await use_case.list_projects(
            organization_id=1,
            status=ProjectStatusEnum.ACTIVE,
            page=1,
            page_size=20,
        )

        # Assert
        assert len(projects) == 1
        assert total == 1
        call_args = mock_project_repo.list_by_organization.call_args
        assert call_args.kwargs["status"] == ProjectStatus.ACTIVE

    async def test_list_projects_pagination(self) -> None:
        """正常系：ページネーションが正しく動作する"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_projects = [Mock(spec=ProjectEntity, id=i) for i in range(20)]
        mock_project_repo.list_by_organization = AsyncMock(return_value=mock_projects)
        mock_project_repo.count_by_organization = AsyncMock(return_value=100)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        projects, total = await use_case.list_projects(
            organization_id=1,
            page=3,  # 3ページ目
            page_size=20,
        )

        # Assert
        assert len(projects) == 20
        assert total == 100
        mock_project_repo.list_by_organization.assert_called_once_with(
            organization_id=1,
            client_organization_id=None,
            status=None,
            skip=40,  # (3-1) * 20
            limit=20,
            include_deleted=False,
        )

    async def test_list_projects_page_size_limit(self) -> None:
        """正常系：ページサイズが100を超える場合、100に制限される"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_projects = []
        mock_project_repo.list_by_organization = AsyncMock(return_value=mock_projects)
        mock_project_repo.count_by_organization = AsyncMock(return_value=0)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        await use_case.list_projects(
            organization_id=1,
            page=1,
            page_size=150,  # 100を超える
        )

        # Assert
        call_args = mock_project_repo.list_by_organization.call_args
        assert call_args.kwargs["limit"] == 100


class TestProjectUseCasesUpdate:
    """プロジェクト更新ユースケースのテスト"""

    async def test_update_project_success(self) -> None:
        """正常系：プロジェクトを更新できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="旧プロジェクト名",
            status=ProjectStatus.ACTIVE,
            progress=0,
            total_lists=0,
            completed_lists=0,
            total_submissions=0,
        )
        mock_project_repo.find_by_id = AsyncMock(return_value=mock_project)

        updated_project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="新プロジェクト名",
            status=ProjectStatus.ACTIVE,
            progress=0,
            total_lists=0,
            completed_lists=0,
            total_submissions=0,
        )
        mock_project_repo.update = AsyncMock(return_value=updated_project)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act
        project = await use_case.update_project(
            project_id=1,
            organization_id=1,
            request=request,
        )

        # Assert
        assert project.name == "新プロジェクト名"
        mock_project_repo.update.assert_called_once()

    async def test_update_project_not_found(self) -> None:
        """異常系：プロジェクトが見つからない場合、エラー"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()
        mock_project_repo.find_by_id = AsyncMock(return_value=None)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await use_case.update_project(
                project_id=999,
                organization_id=1,
                request=request,
            )

    async def test_update_project_cannot_edit_archived(self) -> None:
        """異常系：アーカイブ済みプロジェクトは編集不可"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="アーカイブ済みプロジェクト",
            status=ProjectStatus.ARCHIVED,
            progress=0,
            total_lists=0,
            completed_lists=0,
            total_submissions=0,
        )
        mock_project_repo.find_by_id = AsyncMock(return_value=mock_project)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act & Assert
        with pytest.raises(ProjectCannotBeEditedError):
            await use_case.update_project(
                project_id=1,
                organization_id=1,
                request=request,
            )

    async def test_update_project_validation_error(self) -> None:
        """異常系：無効なデータの場合、バリデーションエラー"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_project = ProjectEntity(
            id=1,
            organization_id=1,
            client_organization_id=10,
            name="テストプロジェクト",
            status=ProjectStatus.ACTIVE,
            progress=0,
            total_lists=100,
            completed_lists=150,  # 無効：完了リスト数が総リスト数を超える
            total_submissions=0,
        )
        mock_project_repo.find_by_id = AsyncMock(return_value=mock_project)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        request = ProjectUpdateRequest(name="新プロジェクト名")

        # Act & Assert
        with pytest.raises(ProjectValidationError):
            await use_case.update_project(
                project_id=1,
                organization_id=1,
                request=request,
            )


class TestProjectUseCasesDelete:
    """プロジェクト削除ユースケースのテスト"""

    async def test_delete_project_success(self) -> None:
        """正常系：プロジェクトを削除できる"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()

        mock_project = Mock(spec=ProjectEntity)
        mock_project.id = 1
        mock_project_repo.find_by_id = AsyncMock(return_value=mock_project)
        mock_project_repo.soft_delete = AsyncMock()

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act
        await use_case.delete_project(
            project_id=1,
            organization_id=1,
        )

        # Assert
        mock_project_repo.find_by_id.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )
        mock_project_repo.soft_delete.assert_called_once_with(
            project_id=1,
            requesting_organization_id=1,
        )

    async def test_delete_project_not_found(self) -> None:
        """異常系：プロジェクトが見つからない場合、エラー"""
        # Arrange
        mock_project_repo = AsyncMock()
        mock_client_org_repo = AsyncMock()
        mock_project_repo.find_by_id = AsyncMock(return_value=None)

        use_case = ProjectUseCases(mock_project_repo, mock_client_org_repo)

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            await use_case.delete_project(
                project_id=999,
                organization_id=1,
            )
