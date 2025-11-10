"""
顧客組織リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.client_organization_entity import ClientOrganizationEntity


class IClientOrganizationRepository(ABC):
    """
    顧客組織リポジトリインターフェース

    顧客組織の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        organization_id: int,
        industry: str | None = None,
        employee_count: int | None = None,
        annual_revenue: int | None = None,
        established_year: int | None = None,
        website: str | None = None,
        sales_person: str | None = None,
        notes: str | None = None,
    ) -> ClientOrganizationEntity:
        """
        顧客組織を作成

        Args:
            organization_id: 対応するOrganizationのID
            industry: 業種
            employee_count: 従業員数
            annual_revenue: 年商（円）
            established_year: 設立年
            website: Webサイト
            sales_person: 担当営業
            notes: 備考

        Returns:
            ClientOrganizationEntity: 作成された顧客組織エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
    ) -> ClientOrganizationEntity | None:
        """
        IDで顧客組織を検索（マルチテナント対応）

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ClientOrganizationEntity | None: 見つかった場合は顧客組織エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def find_by_organization_id(
        self,
        organization_id: int,
        requesting_organization_id: int,
    ) -> ClientOrganizationEntity | None:
        """
        組織IDで顧客組織を検索（マルチテナント対応）

        Args:
            organization_id: 組織ID（organizations.id）
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ClientOrganizationEntity | None: 見つかった場合は顧客組織エンティティ、見つからない場合はNone

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
        include_deleted: bool = False,
    ) -> list[ClientOrganizationEntity]:
        """
        営業支援会社に属する顧客組織の一覧を取得

        Args:
            sales_support_organization_id: 営業支援会社の組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み顧客組織を含めるか

        Returns:
            list[ClientOrganizationEntity]: 顧客組織エンティティのリスト
        """
        pass

    @abstractmethod
    async def update(
        self,
        client_organization: ClientOrganizationEntity,
        requesting_organization_id: int,
    ) -> ClientOrganizationEntity:
        """
        顧客組織情報を更新（マルチテナント対応）

        Args:
            client_organization: 更新する顧客組織エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ClientOrganizationEntity: 更新された顧客組織エンティティ

        Raises:
            ClientOrganizationNotFoundError: 顧客組織が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        顧客組織を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ClientOrganizationNotFoundError: 顧客組織が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
