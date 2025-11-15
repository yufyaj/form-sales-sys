"""
プロジェクト管理APIルーター

プロジェクトのCRUD操作のエンドポイントを提供します
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.application.use_cases.project_use_cases import ProjectUseCases
from src.domain.entities.project_entity import ProjectEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)
from src.domain.interfaces.project_repository import IProjectRepository
from src.infrastructure.persistence.repositories.client_organization_repository import (
    ClientOrganizationRepository,
)
from src.infrastructure.persistence.repositories.project_repository import (
    ProjectRepository,
)

router = APIRouter(prefix="/projects", tags=["projects"])


async def get_project_use_cases(
    session: AsyncSession = Depends(get_db),
) -> ProjectUseCases:
    """
    プロジェクトユースケースの依存性注入

    Args:
        session: データベースセッション

    Returns:
        ProjectUseCases: プロジェクトユースケースのインスタンス
    """
    project_repo: IProjectRepository = ProjectRepository(session)
    client_org_repo: IClientOrganizationRepository = ClientOrganizationRepository(
        session
    )
    return ProjectUseCases(
        project_repository=project_repo,
        client_organization_repository=client_org_repo,
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="プロジェクト作成",
    description="新規プロジェクトを作成します。認証が必要です。",
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
) -> ProjectResponse:
    """
    新規プロジェクトを作成

    - **name**: プロジェクト名（最大100文字）
    - **description**: プロジェクト説明（最大500文字、省略可）
    - **client_organization_id**: 顧客組織ID
    - **status**: プロジェクトステータス（デフォルト: planning）
    """
    project = await use_cases.create_project(
        organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(project)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="プロジェクト取得",
    description="指定されたIDのプロジェクトを取得します。認証が必要です。",
)
async def get_project(
    project_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
) -> ProjectResponse:
    """
    プロジェクトを取得

    - **project_id**: プロジェクトID
    """
    project = await use_cases.get_project(
        project_id=project_id,
        organization_id=current_user.organization_id,
    )
    return _to_response(project)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="プロジェクト一覧取得",
    description="プロジェクト一覧を取得します。顧客フィルタとステータスフィルタに対応しています。",
)
async def list_projects(
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
    client_organization_id: Annotated[
        int | None,
        Query(description="顧客組織ID（フィルタ用、省略時は全顧客）"),
    ] = None,
    status: Annotated[
        ProjectStatusEnum | None,
        Query(description="プロジェクトステータス（フィルタ用、省略時は全ステータス）"),
    ] = None,
    page: Annotated[int, Query(ge=1, description="ページ番号（1始まり）")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="ページサイズ（最大100）")
    ] = 20,
) -> ProjectListResponse:
    """
    プロジェクト一覧を取得

    - **client_organization_id**: 顧客組織ID（フィルタ用、省略時は全顧客）
    - **status**: プロジェクトステータス（フィルタ用、省略時は全ステータス）
    - **page**: ページ番号（デフォルト: 1）
    - **page_size**: ページサイズ（デフォルト: 20、最大: 100）
    """
    projects, total = await use_cases.list_projects(
        organization_id=current_user.organization_id,
        client_organization_id=client_organization_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    return ProjectListResponse(
        projects=[_to_response(project) for project in projects],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="プロジェクト更新",
    description="プロジェクト情報を更新します。アーカイブ済みまたは削除済みのプロジェクトは編集できません。",
)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
) -> ProjectResponse:
    """
    プロジェクト情報を更新

    - **project_id**: プロジェクトID
    - **name**: プロジェクト名（省略可）
    - **description**: プロジェクト説明（省略可）
    - **status**: プロジェクトステータス（省略可）

    注意: アーカイブ済みまたは削除済みのプロジェクトは編集できません。
    """
    project = await use_cases.update_project(
        project_id=project_id,
        organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="プロジェクト削除",
    description="プロジェクトを論理削除します。",
)
async def delete_project(
    project_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
) -> None:
    """
    プロジェクトを論理削除

    - **project_id**: プロジェクトID
    """
    await use_cases.delete_project(
        project_id=project_id,
        organization_id=current_user.organization_id,
    )


def _to_response(project: ProjectEntity) -> ProjectResponse:
    """
    ProjectEntityをProjectResponseに変換

    Args:
        project: プロジェクトエンティティ

    Returns:
        ProjectResponse: プロジェクトレスポンス
    """
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        client_organization_id=project.client_organization_id,
        name=project.name,
        description=project.description,
        status=ProjectStatusEnum(project.status.value),
        progress=project.progress,
        total_lists=project.total_lists,
        completed_lists=project.completed_lists,
        total_submissions=project.total_submissions,
        created_at=project.created_at,
        updated_at=project.updated_at,
        deleted_at=project.deleted_at,
    )
