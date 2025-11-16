"""
プロジェクトリポジトリの実装

IProjectRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import date, datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project_entity import ProjectEntity, ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.domain.interfaces.project_repository import IProjectRepository
from src.infrastructure.persistence.models.project import Project


class ProjectRepository(IProjectRepository):
    """
    プロジェクトリポジトリの実装

    SQLAlchemyを使用してプロジェクトの永続化を行います。
    IDOR脆弱性対策として、全てのクエリでsales_support_organization_idによるテナント分離を実施します。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        name: str,
        client_organization_id: int,
        sales_support_organization_id: int,
        status: ProjectStatus = ProjectStatus.PLANNING,
        start_date: date | None = None,
        end_date: date | None = None,
        description: str | None = None,
    ) -> ProjectEntity:
        """プロジェクトを作成"""
        project = Project(
            name=name,
            client_organization_id=client_organization_id,
            sales_support_organization_id=sales_support_organization_id,
            status=status.value,  # EnumをStringに変換
            start_date=start_date,
            end_date=end_date,
            description=description,
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
        """
        IDでプロジェクトを検索（マルチテナント対応・IDOR脆弱性対策）

        sales_support_organization_idによるテナント分離を実施します。
        """
        stmt = select(Project).where(
            Project.id == project_id,
            Project.sales_support_organization_id == requesting_organization_id,
            Project.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            return None

        return self._to_entity(project)

    async def list_by_sales_support_organization(
        self,
        sales_support_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status: ProjectStatus | None = None,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """営業支援会社に属するプロジェクトの一覧を取得"""
        conditions = [
            Project.sales_support_organization_id == sales_support_organization_id,
        ]

        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))

        if status is not None:
            conditions.append(Project.status == status.value)

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

    async def list_by_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """
        顧客組織に属するプロジェクトの一覧を取得（マルチテナント対応・IDOR脆弱性対策）

        sales_support_organization_idによるテナント分離を実施します。
        """
        conditions = [
            Project.client_organization_id == client_organization_id,
            Project.sales_support_organization_id == requesting_organization_id,
        ]

        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))

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

    async def update(
        self,
        project: ProjectEntity,
        requesting_organization_id: int,
    ) -> ProjectEntity:
        """
        プロジェクト情報を更新（マルチテナント対応・IDOR脆弱性対策）

        sales_support_organization_idによるテナント分離を実施します。
        """
        stmt = select(Project).where(
            Project.id == project.id,
            Project.sales_support_organization_id == requesting_organization_id,
            Project.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if db_project is None:
            raise ProjectNotFoundError(project.id)

        # エンティティの値でモデルを更新
        db_project.name = project.name
        db_project.client_organization_id = project.client_organization_id
        db_project.status = project.status.value
        db_project.start_date = project.start_date
        db_project.end_date = project.end_date
        db_project.description = project.description

        await self._session.flush()
        await self._session.refresh(db_project)

        return self._to_entity(db_project)

    async def soft_delete(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        プロジェクトを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）

        sales_support_organization_idによるテナント分離を実施します。
        """
        stmt = select(Project).where(
            Project.id == project_id,
            Project.sales_support_organization_id == requesting_organization_id,
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
            name=project.name,
            client_organization_id=project.client_organization_id,
            sales_support_organization_id=project.sales_support_organization_id,
            status=ProjectStatus(project.status),  # StringをEnumに変換
            start_date=project.start_date,
            end_date=project.end_date,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            deleted_at=project.deleted_at,
        )
