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
    ProjectPriorityEnum,
    ProjectResponse,
    ProjectStatusEnum,
    ProjectUpdateRequest,
)
from src.application.use_cases.project_use_cases import ProjectUseCases
from src.domain.entities.project_entity import ProjectEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.project_repository import IProjectRepository
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
    return ProjectUseCases(
        project_repository=project_repo,
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

    - **name**: プロジェクト名（最大255文字）
    - **description**: プロジェクト説明（省略可）
    - **client_organization_id**: 顧客組織ID
    - **status**: プロジェクトステータス（デフォルト: planning）
    - **start_date**: 開始予定日（省略可）
    - **end_date**: 終了予定日（省略可）
    - **estimated_budget**: 見積予算（円、省略可）
    - **actual_budget**: 実績予算（円、省略可）
    - **priority**: プロジェクト優先度（省略可）
    - **owner_user_id**: プロジェクトオーナー（担当ユーザーID、省略可）
    - **notes**: 備考（省略可）
    """
    project = await use_cases.create_project(
        requesting_organization_id=current_user.organization_id,
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
        requesting_organization_id=current_user.organization_id,
    )
    return _to_response(project)


@router.get(
    "/client/{client_organization_id}",
    response_model=ProjectListResponse,
    summary="顧客別プロジェクト一覧取得",
    description="指定された顧客組織に属するプロジェクト一覧を取得します。",
)
async def list_projects_by_client(
    client_organization_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
    page: Annotated[int, Query(ge=1, description="ページ番号（1始まり）")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="ページサイズ（最大100）")
    ] = 20,
) -> ProjectListResponse:
    """
    顧客組織に属するプロジェクト一覧を取得

    - **client_organization_id**: 顧客組織ID
    - **page**: ページ番号（デフォルト: 1）
    - **page_size**: ページサイズ（デフォルト: 20、最大: 100）
    """
    projects, total = await use_cases.list_projects_by_client(
        client_organization_id=client_organization_id,
        requesting_organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
    )

    return ProjectListResponse(
        projects=[_to_response(project) for project in projects],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="営業支援会社別プロジェクト一覧取得",
    description="営業支援会社に属する全顧客のプロジェクト一覧を取得します。ステータスフィルタに対応しています。",
)
async def list_projects_by_sales_support(
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: ProjectUseCases = Depends(get_project_use_cases),
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
    営業支援会社に属する全顧客のプロジェクト一覧を取得

    - **status**: プロジェクトステータス（フィルタ用、省略時は全ステータス）
    - **page**: ページ番号（デフォルト: 1）
    - **page_size**: ページサイズ（デフォルト: 20、最大: 100）
    """
    projects, total = await use_cases.list_projects_by_sales_support(
        sales_support_organization_id=current_user.organization_id,
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
    description="プロジェクト情報を更新します。",
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
    - **start_date**: 開始予定日（省略可）
    - **end_date**: 終了予定日（省略可）
    - **estimated_budget**: 見積予算（円、省略可）
    - **actual_budget**: 実績予算（円、省略可）
    - **priority**: プロジェクト優先度（省略可）
    - **owner_user_id**: プロジェクトオーナー（担当ユーザーID、省略可）
    - **notes**: 備考（省略可）
    """
    project = await use_cases.update_project(
        project_id=project_id,
        requesting_organization_id=current_user.organization_id,
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
        requesting_organization_id=current_user.organization_id,
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
        client_organization_id=project.client_organization_id,
        name=project.name,
        description=project.description,
        status=ProjectStatusEnum(project.status.value),
        start_date=project.start_date,
        end_date=project.end_date,
        estimated_budget=project.estimated_budget,
        actual_budget=project.actual_budget,
        priority=ProjectPriorityEnum(project.priority.value) if project.priority else None,
        owner_user_id=project.owner_user_id,
        notes=project.notes,
        created_at=project.created_at,
        updated_at=project.updated_at,
        deleted_at=project.deleted_at,
    )
