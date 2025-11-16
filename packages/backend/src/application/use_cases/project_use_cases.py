"""
プロジェクト管理のユースケース

プロジェクトのCRUD操作とビジネスロジックを実行します
"""

from datetime import date

from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectPriorityEnum,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.domain.entities.project_entity import (
    ProjectEntity,
    ProjectPriority,
    ProjectStatus,
)
from src.domain.exceptions import (
    ProjectNotFoundError,
)
from src.domain.interfaces.project_repository import IProjectRepository


class ProjectUseCases:
    """プロジェクト管理のユースケースクラス"""

    def __init__(
        self,
        project_repository: IProjectRepository,
    ) -> None:
        """
        Args:
            project_repository: プロジェクトリポジトリ
        """
        self._project_repo = project_repository

    async def create_project(
        self,
        requesting_organization_id: int,
        request: ProjectCreateRequest,
    ) -> ProjectEntity:
        """
        新規プロジェクトを作成

        Args:
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（マルチテナント用）
            request: プロジェクト作成リクエスト

        Returns:
            作成されたプロジェクトエンティティ

        Raises:
            ClientOrganizationNotFoundError: 顧客組織が見つからない場合
            UserNotFoundError: owner_user_idが指定され、そのユーザーが見つからない場合
            InvalidDateRangeError: 日付範囲が不正な場合
            InvalidBudgetError: 予算値が不正な場合
        """
        # ProjectStatusEnumをProjectStatusに変換
        status = ProjectStatus(request.status.value)

        # ProjectPriorityEnumをProjectPriorityに変換（Noneの場合はそのまま）
        priority_value = request.priority.value if request.priority else None

        # プロジェクトを作成（repositoryで顧客組織の存在確認・ユーザー検証を実施）
        project = await self._project_repo.create(
            client_organization_id=request.client_organization_id,
            requesting_organization_id=requesting_organization_id,
            name=request.name,
            status=status,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            estimated_budget=request.estimated_budget,
            actual_budget=request.actual_budget,
            priority=priority_value,
            owner_user_id=request.owner_user_id,
            notes=request.notes,
        )

        return project

    async def get_project(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> ProjectEntity:
        """
        プロジェクトを取得

        Args:
            project_id: プロジェクトID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（マルチテナント対応）

        Returns:
            プロジェクトエンティティ

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
        """
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=requesting_organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        return project

    async def list_projects_by_client(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProjectEntity], int]:
        """
        顧客組織に属するプロジェクト一覧を取得

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（マルチテナント用）
            page: ページ番号（1始まり）
            page_size: ページサイズ（最大100）

        Returns:
            (プロジェクトリスト, 総件数)のタプル
        """
        # ページサイズの制限
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size

        # プロジェクト一覧を取得
        projects = await self._project_repo.list_by_client_organization(
            client_organization_id=client_organization_id,
            requesting_organization_id=requesting_organization_id,
            skip=skip,
            limit=page_size,
            include_deleted=False,
        )

        # 総件数は取得したプロジェクト数を返す（簡易実装）
        # より正確な総件数が必要な場合は、repositoryにcount_by_client_organizationメソッドを追加
        total = len(projects)

        return projects, total

    async def list_projects_by_sales_support(
        self,
        sales_support_organization_id: int,
        status: ProjectStatusEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProjectEntity], int]:
        """
        営業支援会社に属する全顧客のプロジェクト一覧を取得

        Args:
            sales_support_organization_id: 営業支援会社の組織ID
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
        projects = await self._project_repo.list_by_sales_support_organization(
            sales_support_organization_id=sales_support_organization_id,
            skip=skip,
            limit=page_size,
            status_filter=domain_status,
            include_deleted=False,
        )

        # 総件数は取得したプロジェクト数を返す（簡易実装）
        total = len(projects)

        return projects, total

    async def update_project(
        self,
        project_id: int,
        requesting_organization_id: int,
        request: ProjectUpdateRequest,
    ) -> ProjectEntity:
        """
        プロジェクト情報を更新

        Args:
            project_id: プロジェクトID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新されたプロジェクトエンティティ

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
            UserNotFoundError: owner_user_idが指定され、そのユーザーが見つからない場合
            InvalidDateRangeError: 日付範囲が不正な場合
            InvalidBudgetError: 予算値が不正な場合
        """
        # プロジェクトを取得
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=requesting_organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        # フィールドを更新
        if request.name is not None:
            project.name = request.name

        if request.description is not None:
            project.description = request.description

        if request.status is not None:
            project.status = ProjectStatus(request.status.value)

        if request.start_date is not None:
            project.start_date = request.start_date

        if request.end_date is not None:
            project.end_date = request.end_date

        if request.estimated_budget is not None:
            project.estimated_budget = request.estimated_budget

        if request.actual_budget is not None:
            project.actual_budget = request.actual_budget

        if request.priority is not None:
            project.priority = ProjectPriority(request.priority.value)

        if request.owner_user_id is not None:
            project.owner_user_id = request.owner_user_id

        if request.notes is not None:
            project.notes = request.notes

        # リポジトリで永続化（バリデーションはrepositoryで実施）
        updated_project = await self._project_repo.update(
            project=project,
            requesting_organization_id=requesting_organization_id,
        )

        return updated_project

    async def delete_project(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        プロジェクトを論理削除

        Args:
            project_id: プロジェクトID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（マルチテナント対応）

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合
        """
        # プロジェクトの存在確認
        project = await self._project_repo.find_by_id(
            project_id=project_id,
            requesting_organization_id=requesting_organization_id,
        )
        if project is None:
            raise ProjectNotFoundError(project_id)

        # 論理削除を実行
        await self._project_repo.soft_delete(
            project_id=project_id,
            requesting_organization_id=requesting_organization_id,
        )
