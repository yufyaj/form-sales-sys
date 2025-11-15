"""
営業支援会社担当者リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.sales_company_staff_entity import SalesCompanyStaffEntity


class ISalesCompanyStaffRepository(ABC):
    """
    営業支援会社担当者リポジトリインターフェース

    営業支援会社担当者の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        user_id: int,
        organization_id: int,
        department: str | None = None,
        position: str | None = None,
        employee_number: str | None = None,
        notes: str | None = None,
    ) -> SalesCompanyStaffEntity:
        """
        営業支援会社担当者を作成

        Args:
            user_id: 対応するUserのID
            organization_id: 営業支援会社の組織ID
            department: 部署
            position: 役職
            employee_number: 社員番号
            notes: 備考

        Returns:
            SalesCompanyStaffEntity: 作成された営業支援会社担当者エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        staff_id: int,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity | None:
        """
        IDで営業支援会社担当者を検索（マルチテナント対応）

        Args:
            staff_id: 営業支援会社担当者ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            SalesCompanyStaffEntity | None: 見つかった場合は担当者エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: int,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity | None:
        """
        ユーザーIDで営業支援会社担当者を検索（マルチテナント対応）

        Args:
            user_id: ユーザーID（users.id）
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            SalesCompanyStaffEntity | None: 見つかった場合は担当者エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[SalesCompanyStaffEntity]:
        """
        営業支援会社に属する担当者の一覧を取得

        Args:
            organization_id: 営業支援会社の組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み担当者を含めるか

        Returns:
            list[SalesCompanyStaffEntity]: 担当者エンティティのリスト
        """
        pass

    @abstractmethod
    async def count_by_organization(
        self,
        organization_id: int,
        include_deleted: bool = False,
    ) -> int:
        """
        営業支援会社に属する担当者の総件数を取得

        Args:
            organization_id: 営業支援会社の組織ID
            include_deleted: 削除済み担当者を含めるか

        Returns:
            int: 担当者の総件数
        """
        pass

    @abstractmethod
    async def update(
        self,
        staff: SalesCompanyStaffEntity,
        requesting_organization_id: int,
    ) -> SalesCompanyStaffEntity:
        """
        営業支援会社担当者情報を更新（マルチテナント対応）

        Args:
            staff: 更新する担当者エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            SalesCompanyStaffEntity: 更新された担当者エンティティ

        Raises:
            SalesCompanyStaffNotFoundError: 担当者が見つからない場合、
                                           またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        staff_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        営業支援会社担当者を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            staff_id: 営業支援会社担当者ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            SalesCompanyStaffNotFoundError: 担当者が見つからない場合、
                                           またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
