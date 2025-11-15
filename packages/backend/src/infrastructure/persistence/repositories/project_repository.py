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
from src.infrastructure.persistence.models.client_organization import (
    ClientOrganization,
)
from src.infrastructure.persistence.models.organization import Organization
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
        client_organization_id: int,
        requesting_organization_id: int,
        name: str,
        status: ProjectStatus,
        description: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        estimated_budget: int | None = None,
        actual_budget: int | None = None,
        priority: str | None = None,
        owner_user_id: int | None = None,
        notes: str | None = None,
    ) -> ProjectEntity:
        """プロジェクトを作成（マルチテナント対応・IDOR脆弱性対策）"""
        # client_organization_idがrequesting_organization_id配下か検証
        from src.domain.exceptions import ClientOrganizationNotFoundError, UserNotFoundError

        stmt = (
            select(ClientOrganization)
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(
                ClientOrganization.id == client_organization_id,
                ClientOrganization.deleted_at.is_(None),
                Organization.parent_organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        client_org = result.scalar_one_or_none()

        if client_org is None:
            raise ClientOrganizationNotFoundError(client_organization_id)

        # owner_user_idが指定されている場合、requesting_organization_id配下のユーザーか検証
        if owner_user_id is not None:
            from src.infrastructure.persistence.models.user import User
            from sqlalchemy import or_

            user_stmt = (
                select(User)
                .join(Organization, User.organization_id == Organization.id)
                .where(
                    User.id == owner_user_id,
                    or_(
                        Organization.id == requesting_organization_id,
                        Organization.parent_organization_id == requesting_organization_id,
                    ),
                    User.deleted_at.is_(None),
                    Organization.deleted_at.is_(None),
                )
            )
            user_result = await self._session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundError(owner_user_id)

        # 日付範囲と予算値のバリデーション
        from src.domain.exceptions import InvalidBudgetError, InvalidDateRangeError

        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise InvalidDateRangeError(str(start_date), str(end_date))

        if estimated_budget is not None and estimated_budget < 0:
            raise InvalidBudgetError("見積予算", estimated_budget)

        if actual_budget is not None and actual_budget < 0:
            raise InvalidBudgetError("実績予算", actual_budget)

        project = Project(
            client_organization_id=client_organization_id,
            name=name,
            status=status,
            description=description,
            start_date=start_date,
            end_date=end_date,
            estimated_budget=estimated_budget,
            actual_budget=actual_budget,
            priority=priority,
            owner_user_id=owner_user_id,
            notes=notes,
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
        stmt = (
            select(Project)
            .join(
                ClientOrganization,
                Project.client_organization_id == ClientOrganization.id,
            )
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(
                Project.id == project_id,
                Project.deleted_at.is_(None),
                Organization.parent_organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            return None

        return self._to_entity(project)

    async def list_by_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """顧客組織に属するプロジェクトの一覧を取得（マルチテナント対応・IDOR脆弱性対策）"""
        conditions = [
            Project.client_organization_id == client_organization_id,
            Organization.parent_organization_id == requesting_organization_id,
        ]

        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))
            conditions.append(ClientOrganization.deleted_at.is_(None))
            conditions.append(Organization.deleted_at.is_(None))

        stmt = (
            select(Project)
            .join(
                ClientOrganization,
                Project.client_organization_id == ClientOrganization.id,
            )
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )

        result = await self._session.execute(stmt)
        projects = result.scalars().all()

        return [self._to_entity(p) for p in projects]

    async def list_by_sales_support_organization(
        self,
        sales_support_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status_filter: ProjectStatus | None = None,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """営業支援会社に属する全顧客のプロジェクト一覧を取得"""
        conditions = [
            Organization.parent_organization_id == sales_support_organization_id,
        ]

        if status_filter is not None:
            conditions.append(Project.status == status_filter)

        if not include_deleted:
            conditions.append(Project.deleted_at.is_(None))
            conditions.append(ClientOrganization.deleted_at.is_(None))
            conditions.append(Organization.deleted_at.is_(None))

        stmt = (
            select(Project)
            .join(
                ClientOrganization,
                Project.client_organization_id == ClientOrganization.id,
            )
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
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
        """プロジェクト情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        from src.domain.exceptions import UserNotFoundError
        from src.infrastructure.persistence.models.user import User
        from sqlalchemy import or_

        stmt = (
            select(Project)
            .join(
                ClientOrganization,
                Project.client_organization_id == ClientOrganization.id,
            )
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(
                Project.id == project.id,
                Project.deleted_at.is_(None),
                Organization.parent_organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if db_project is None:
            raise ProjectNotFoundError(project.id)

        # owner_user_idが指定されている場合、requesting_organization_id配下のユーザーか検証
        if project.owner_user_id is not None:
            user_stmt = (
                select(User)
                .join(Organization, User.organization_id == Organization.id)
                .where(
                    User.id == project.owner_user_id,
                    or_(
                        Organization.id == requesting_organization_id,
                        Organization.parent_organization_id == requesting_organization_id,
                    ),
                    User.deleted_at.is_(None),
                    Organization.deleted_at.is_(None),
                )
            )
            user_result = await self._session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundError(project.owner_user_id)

        # プロジェクトエンティティのバリデーション
        project.validate()

        # エンティティの値でモデルを更新
        db_project.name = project.name
        db_project.status = project.status
        db_project.description = project.description
        db_project.start_date = project.start_date
        db_project.end_date = project.end_date
        db_project.estimated_budget = project.estimated_budget
        db_project.actual_budget = project.actual_budget
        db_project.priority = project.priority
        db_project.owner_user_id = project.owner_user_id
        db_project.notes = project.notes

        await self._session.flush()
        await self._session.refresh(db_project)

        return self._to_entity(db_project)

    async def soft_delete(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> None:
        """プロジェクトを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = (
            select(Project)
            .join(
                ClientOrganization,
                Project.client_organization_id == ClientOrganization.id,
            )
            .join(
                Organization,
                ClientOrganization.organization_id == Organization.id,
            )
            .where(
                Project.id == project_id,
                Project.deleted_at.is_(None),
                Organization.parent_organization_id == requesting_organization_id,
            )
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
            client_organization_id=project.client_organization_id,
            name=project.name,
            status=project.status,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            estimated_budget=project.estimated_budget,
            actual_budget=project.actual_budget,
            priority=project.priority,
            owner_user_id=project.owner_user_id,
            notes=project.notes,
            created_at=project.created_at,
            updated_at=project.updated_at,
            deleted_at=project.deleted_at,
        )
