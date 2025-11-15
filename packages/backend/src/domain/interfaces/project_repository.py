"""
プロジェクトリポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.project_entity import ProjectEntity, ProjectStatus


class IProjectRepository(ABC):
    """
    プロジェクトリポジトリインターフェース

    プロジェクトの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        organization_id: int,
        client_organization_id: int,
        name: str,
        description: str | None = None,
        status: ProjectStatus = ProjectStatus.PLANNING,
    ) -> ProjectEntity:
        """
        プロジェクトを作成

        Args:
            organization_id: 営業支援組織ID（マルチテナント用）
            client_organization_id: 顧客組織ID
            name: プロジェクト名（最大100文字）
            description: プロジェクト説明
            status: プロジェクトステータス

        Returns:
            ProjectEntity: 作成されたプロジェクトエンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> ProjectEntity | None:
        """
        IDでプロジェクトを検索（マルチテナント対応）

        Args:
            project_id: プロジェクトID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ProjectEntity | None: 見つかった場合はプロジェクトエンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: int,
        client_organization_id: int | None = None,
        status: ProjectStatus | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """
        営業支援組織に属するプロジェクト一覧を取得（顧客フィルタ対応）

        Args:
            organization_id: 営業支援組織ID（マルチテナント用）
            client_organization_id: 顧客組織ID（フィルタ用、Noneの場合は全顧客）
            status: プロジェクトステータス（フィルタ用、Noneの場合は全ステータス）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済みプロジェクトを含めるか

        Returns:
            list[ProjectEntity]: プロジェクトエンティティのリスト
        """
        pass

    @abstractmethod
    async def count_by_organization(
        self,
        organization_id: int,
        client_organization_id: int | None = None,
        status: ProjectStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        営業支援組織に属するプロジェクト数を取得（顧客フィルタ対応）

        Args:
            organization_id: 営業支援組織ID（マルチテナント用）
            client_organization_id: 顧客組織ID（フィルタ用、Noneの場合は全顧客）
            status: プロジェクトステータス（フィルタ用、Noneの場合は全ステータス）
            include_deleted: 削除済みプロジェクトを含めるか

        Returns:
            int: プロジェクト数
        """
        pass

    @abstractmethod
    async def update(
        self,
        project: ProjectEntity,
        requesting_organization_id: int,
    ) -> ProjectEntity:
        """
        プロジェクト情報を更新（マルチテナント対応）

        Args:
            project: 更新するプロジェクトエンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ProjectEntity: 更新されたプロジェクトエンティティ

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合、
                                 またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        project_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        プロジェクトを論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            project_id: プロジェクトID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ProjectNotFoundError: プロジェクトが見つからない場合、
                                 またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
