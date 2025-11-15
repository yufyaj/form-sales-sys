"""
プロジェクトリポジトリの実装

IProjectRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project_entity import ProjectEntity, ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.domain.interfaces.project_repository import IProjectRepository
from src.infrastructure.persistence.models.project import Project


class ProjectRepository(IProjectRepository):
    """
    プロジェクトリポジトリの実装

    SQLAlchemyを使用してプロジェクトの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        organization_id: int,
        client_organization_id: int,
        name: str,
        description: str | None = None,
        status: ProjectStatus = ProjectStatus.PLANNING,
    ) -> ProjectEntity:
        """プロジェクトを作成"""
        project = Project(
            organization_id=organization_id,
            client_organization_id=client_organization_id,
            name=name,
            description=description,
            status=status,
            progress=0,
            total_lists=0,
            completed_lists=0,
            total_submissions=0,
        )

        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)

        return self._to_entity(project)

    async def find_by_id(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> ProjectEntity | None:
        """IDでプロジェクトを検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Project).where(
            Project.id == project_id,
            Project.organization_id == requesting_organization_id,
            Project.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            return None

        return self._to_entity(project)

    async def list_by_organization(
        self,
        organization_id: int,
        client_organization_id: int | None = None,
        status: ProjectStatus | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """営業支援組織に属するプロジェクト一覧を取得（顧客フィルタ対応）"""
        conditions = [Project.organization_id == organization_id]

        # 削除済みフィルタ
        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))

        # 顧客組織フィルタ
        if client_organization_id is not None:
            conditions.append(Project.client_organization_id == client_organization_id)

        # ステータスフィルタ
        if status is not None:
            conditions.append(Project.status == status)

        stmt = (
            select(Project)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )

        result = await self._session.execute(stmt)
        projects = result.scalars().all()

        return [self._to_entity(p) for p in projects]

    async def count_by_organization(
        self,
        organization_id: int,
        client_organization_id: int | None = None,
        status: ProjectStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """営業支援組織に属するプロジェクト数を取得（顧客フィルタ対応）"""
        conditions = [Project.organization_id == organization_id]

        # 削除済みフィルタ
        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))

        # 顧客組織フィルタ
        if client_organization_id is not None:
            conditions.append(Project.client_organization_id == client_organization_id)

        # ステータスフィルタ
        if status is not None:
            conditions.append(Project.status == status)

        stmt = select(func.count()).select_from(Project).where(and_(*conditions))

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def update(
        self,
        project: ProjectEntity,
        requesting_organization_id: int,
    ) -> ProjectEntity:
        """プロジェクト情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Project).where(
            Project.id == project.id,
            Project.organization_id == requesting_organization_id,
            Project.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if db_project is None:
            raise ProjectNotFoundError(project.id)

        # エンティティの値でモデルを更新
        db_project.name = project.name
        db_project.description = project.description
        db_project.status = project.status
        db_project.progress = project.progress
        db_project.total_lists = project.total_lists
        db_project.completed_lists = project.completed_lists
        db_project.total_submissions = project.total_submissions

        await self._session.flush()
        await self._session.refresh(db_project)

        return self._to_entity(db_project)

    async def soft_delete(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> None:
        """プロジェクトを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(Project).where(
            Project.id == project_id,
            Project.organization_id == requesting_organization_id,
            Project.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            raise ProjectNotFoundError(project_id)

        project.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(self, project: Project) -> ProjectEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ProjectEntity(
            id=project.id,
            organization_id=project.organization_id,
            client_organization_id=project.client_organization_id,
            name=project.name,
            description=project.description,
            status=project.status,
            progress=project.progress,
            total_lists=project.total_lists,
            completed_lists=project.completed_lists,
            total_submissions=project.total_submissions,
            created_at=project.created_at,
            updated_at=project.updated_at,
            deleted_at=project.deleted_at,
        )
