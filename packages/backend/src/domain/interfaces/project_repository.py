"""
プロジェクトリポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities.project_entity import ProjectEntity, ProjectStatus


class IProjectRepository(ABC):
    """
    プロジェクトリポジトリインターフェース

    プロジェクトの永続化操作を定義します。
    """

    @abstractmethod
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
        """
        プロジェクトを作成（マルチテナント対応）

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            name: プロジェクト名
            status: プロジェクトステータス
            description: プロジェクト説明
            start_date: 開始予定日
            end_date: 終了予定日
            estimated_budget: 見積予算（円）
            actual_budget: 実績予算（円）
            priority: プロジェクト優先度
            owner_user_id: プロジェクトオーナー（担当ユーザー）
            notes: 備考

        Returns:
            ProjectEntity: 作成されたプロジェクトエンティティ

        Raises:
            ClientOrganizationNotFoundError: 顧客組織が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合
            UserNotFoundError: owner_user_idが指定され、そのユーザーが見つからない場合、
                              またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
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
    async def list_by_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """
        顧客組織に属するプロジェクトの一覧を取得（マルチテナント対応）

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済みプロジェクトを含めるか

        Returns:
            list[ProjectEntity]: プロジェクトエンティティのリスト

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_sales_support_organization(
        self,
        sales_support_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status_filter: ProjectStatus | None = None,
        include_deleted: bool = False,
    ) -> list[ProjectEntity]:
        """
        営業支援会社に属する全顧客のプロジェクト一覧を取得

        Args:
            sales_support_organization_id: 営業支援会社の組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            status_filter: ステータスでフィルタリング（指定しない場合は全て）
            include_deleted: 削除済みプロジェクトを含めるか

        Returns:
            list[ProjectEntity]: プロジェクトエンティティのリスト
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
