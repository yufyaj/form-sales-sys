"""
プロジェクト管理APIルーター

プロジェクトのCRUD操作のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from src.domain.entities.project_entity import ProjectStatus
from src.domain.entities.user_entity import UserEntity
from src.domain.exceptions import ProjectNotFoundError
from src.infrastructure.persistence.repositories.project_repository import (
    ProjectRepository,
)

router = APIRouter(prefix="/projects", tags=["projects"])


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
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    新規プロジェクトを作成

    認証されたユーザーの所属組織でプロジェクトを作成します。

    - **name**: プロジェクト名
    - **client_organization_id**: 顧客組織ID
    - **status**: ステータス（デフォルト: planning）
    - **start_date**: 開始日（オプション）
    - **end_date**: 終了日（オプション）
    - **description**: 説明（オプション）
    """
    repo = ProjectRepository(db)
    project = await repo.create(
        name=request.name,
        client_organization_id=request.client_organization_id,
        sales_support_organization_id=current_user.organization_id,
        status=request.status,
        start_date=request.start_date,
        end_date=request.end_date,
        description=request.description,
    )
    await db.commit()
    return ProjectResponse.model_validate(project)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="プロジェクト取得",
    description="指定されたIDのプロジェクトを取得します。認証が必要です。",
)
async def get_project(
    project_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    プロジェクトを取得

    認証されたユーザーの所属組織のプロジェクトのみ取得できます。

    - **project_id**: プロジェクトID
    """
    repo = ProjectRepository(db)
    project = await repo.find_by_id(project_id, current_user.organization_id)

    if project is None:
        raise ProjectNotFoundError(project_id)

    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="プロジェクト一覧取得",
    description="プロジェクト一覧を取得します。認証が必要です。",
)
async def list_projects(
    current_user: UserEntity = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    status: ProjectStatus | None = Query(
        None, description="ステータスでフィルタリング（オプション）"
    ),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """
    プロジェクト一覧を取得

    認証されたユーザーの所属組織のプロジェクト一覧を取得します。

    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100、最大: 1000）
    - **status**: ステータスでフィルタリング（オプション）
    """
    repo = ProjectRepository(db)
    projects = await repo.list_by_sales_support_organization(
        current_user.organization_id, skip=skip, limit=limit, status=status
    )

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),  # TODO: 総件数を取得するメソッドを追加
        skip=skip,
        limit=limit,
    )


@router.get(
    "/client/{client_organization_id}",
    response_model=ProjectListResponse,
    summary="顧客組織のプロジェクト一覧取得",
    description="指定された顧客組織に属するプロジェクト一覧を取得します。認証が必要です。",
)
async def list_projects_by_client(
    client_organization_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=1000, description="取得する最大件数"),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """
    顧客組織のプロジェクト一覧を取得

    認証されたユーザーの所属組織のプロジェクトのみ取得できます。

    - **client_organization_id**: 顧客組織ID
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100、最大: 1000）
    """
    repo = ProjectRepository(db)
    projects = await repo.list_by_client_organization(
        client_organization_id,
        current_user.organization_id,
        skip=skip,
        limit=limit,
    )

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=len(projects),  # TODO: 総件数を取得するメソッドを追加
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="プロジェクト更新",
    description="プロジェクト情報を更新します。認証が必要です。",
)
async def update_project(
    project_id: int,
    request: ProjectUpdateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    プロジェクト情報を更新

    認証されたユーザーの所属組織のプロジェクトのみ更新できます。

    - **project_id**: プロジェクトID
    - **request**: 更新内容（部分更新可能）
    """
    repo = ProjectRepository(db)
    project = await repo.find_by_id(project_id, current_user.organization_id)

    if project is None:
        raise ProjectNotFoundError(project_id)

    # 部分更新: リクエストで指定されたフィールドのみ更新
    if request.name is not None:
        project.name = request.name
    if request.client_organization_id is not None:
        project.client_organization_id = request.client_organization_id
    if request.status is not None:
        project.status = request.status
    if request.start_date is not None:
        project.start_date = request.start_date
    if request.end_date is not None:
        project.end_date = request.end_date
    if request.description is not None:
        project.description = request.description

    updated_project = await repo.update(project, current_user.organization_id)
    await db.commit()

    return ProjectResponse.model_validate(updated_project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="プロジェクト削除",
    description="プロジェクトを論理削除します。認証が必要です。",
)
async def delete_project(
    project_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    プロジェクトを論理削除

    認証されたユーザーの所属組織のプロジェクトのみ削除できます。

    - **project_id**: プロジェクトID
    """
    repo = ProjectRepository(db)
    await repo.soft_delete(project_id, current_user.organization_id)
    await db.commit()
