"""
プロジェクト管理のユースケース

プロジェクトのCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.domain.entities.project_entity import ProjectEntity, ProjectStatus
from src.domain.exceptions import (
    ClientOrganizationNotFoundError,
    ProjectCannotBeEditedError,
    ProjectNotFoundError,
    ProjectValidationError,
)
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)
from src.domain.interfaces.project_repository import IProjectRepository


class ProjectUseCases:
    """プロジェクト管理のユースケースクラス"""

    def __init__(
        self,
        project_repository: IProjectRepository,
        client_organization_repository: IClientOrganizationRepository,
    ) -> None:
        """
        Args:
            project_repository: プロジェクトリポジトリ
            client_organization_repository: 顧客組織リポジトリ
        """
        self._project_repo = project_repository
        self._client_org_repo = client_organization_repository

    async def create_project(
        self,
        organization_id: int,
        request: ProjectCreateRequest,
    ) -> ProjectEntity:
        """
        新規プロジェクトを作成

        Args:
            organization_id: 営業支援組織ID（マルチテナント用）
            request: プロジェクト作成リクエスト

        Returns:
            作成されたプロジェクトエンティティ

        Raises:
            ClientOrganizationNotFoundError: 顧客組織が見つからない場合
        """
        # 顧客組織の存在確認（マルチテナント対応）
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id=request.client_organization_id,
            requesting_organization_id=organization_id,
        )
        if client_org is None:
            raise ClientOrganizationNotFoundError(request.client_organization_id)

        # ProjectStatusEnumをProjectStatusに変換
        status = ProjectStatus(request.status.value)

        # プロジェクトを作成
        project = await self._project_repo.create(
            organization_id=organization_id,
            client_organization_id=request.client_organization_id,
            name=request.name,
            description=request.description,
            status=status,
        )

        return project

    async def get_project(
        self,
        project_id: int,
        organization_id: int,
    ) -> ProjectEntity:
        """
        プロジェクトを取得

        Args:
            project_id: プロジェクトID
            organization_id: 営業支援組織ID（マルチテナント対応）

        Returns:
            プロジェクトエンティティ

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
        """
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        return project

    async def list_projects(
        self,
        organization_id: int,
        client_organization_id: int | None = None,
        status: ProjectStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProjectEntity], int]:
        """
        プロジェクト一覧を取得（顧客フィルタ対応）

        Args:
            organization_id: 営業支援組織ID（マルチテナント用）
            client_organization_id: 顧客組織ID（フィルタ用、Noneの場合は全顧客）
            status: プロジェクトステータス（フィルタ用、Noneの場合は全ステータス）
            page: ページ番号（1始まり）
            page_size: ページサイズ（最大100）

        Returns:
            (プロジェクトリスト, 総件数)のタプル
        """
        # ページサイズの制限
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size

        # ProjectStatusEnumをProjectStatusに変換
        domain_status = ProjectStatus(status.value) if status else None

        # プロジェクト一覧を取得
        projects = await self._project_repo.list_by_organization(
            organization_id=organization_id,
            client_organization_id=client_organization_id,
            status=domain_status,
            skip=skip,
            limit=page_size,
            include_deleted=False,
        )

        # 総件数を取得
        total = await self._project_repo.count_by_organization(
            organization_id=organization_id,
            client_organization_id=client_organization_id,
            status=domain_status,
            include_deleted=False,
        )

        return projects, total

    async def update_project(
        self,
        project_id: int,
        organization_id: int,
        request: ProjectUpdateRequest,
    ) -> ProjectEntity:
        """
        プロジェクト情報を更新

        Args:
            project_id: プロジェクトID
            organization_id: 営業支援組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新されたプロジェクトエンティティ

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
            ProjectCannotBeEditedError: プロジェクトが編集不可能な状態の場合
            ProjectValidationError: バリデーションエラー
        """
        # プロジェクトを取得
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        # 編集可能かチェック
        if not project.can_be_edited():
            raise ProjectCannotBeEditedError(
                project_id,
                "Project is archived or deleted",
            )

        # フィールドを更新
        if request.name is not None:
            project.name = request.name

        if request.description is not None:
            project.description = request.description

        if request.status is not None:
            project.status = ProjectStatus(request.status.value)

        # エンティティのバリデーション
        if not project.is_valid():
            raise ProjectValidationError(
                "Project validation failed",
                {
                    "progress": project.progress,
                    "total_lists": project.total_lists,
                    "completed_lists": project.completed_lists,
                    "total_submissions": project.total_submissions,
                },
            )

        # リポジトリで永続化
        updated_project = await self._project_repo.update(
            project=project,
            requesting_organization_id=organization_id,
        )

        return updated_project

    async def delete_project(
        self,
        project_id: int,
        organization_id: int,
    ) -> None:
        """
        プロジェクトを論理削除

        Args:
            project_id: プロジェクトID
            organization_id: 営業支援組織ID（マルチテナント対応）

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
        """
        # プロジェクトの存在確認
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        # 論理削除を実行
        await self._project_repo.soft_delete(
            project_id=project_id,
            requesting_organization_id=organization_id,
        )
