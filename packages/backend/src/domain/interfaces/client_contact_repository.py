"""
顧客担当者リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.client_contact_entity import ClientContactEntity


class IClientContactRepository(ABC):
    """
    顧客担当者リポジトリインターフェース

    顧客担当者の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        client_organization_id: int,
        full_name: str,
        department: str | None = None,
        position: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        mobile: str | None = None,
        is_primary: bool = False,
        notes: str | None = None,
    ) -> ClientContactEntity:
        """
        顧客担当者を作成

        Args:
            client_organization_id: 顧客組織ID
            full_name: 氏名
            department: 部署
            position: 役職
            email: メールアドレス
            phone: 電話番号
            mobile: 携帯電話番号
            is_primary: 主担当フラグ
            notes: 備考

        Returns:
            ClientContactEntity: 作成された顧客担当者エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(self, client_contact_id: int) -> ClientContactEntity | None:
        """
        IDで顧客担当者を検索

        Args:
            client_contact_id: 顧客担当者ID

        Returns:
            ClientContactEntity | None: 見つかった場合は顧客担当者エンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def list_by_client_organization(
        self,
        client_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ClientContactEntity]:
        """
        顧客組織に属する担当者の一覧を取得

        Args:
            client_organization_id: 顧客組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み担当者を含めるか

        Returns:
            list[ClientContactEntity]: 顧客担当者エンティティのリスト
        """
        pass

    @abstractmethod
    async def find_primary_contact(
        self, client_organization_id: int
    ) -> ClientContactEntity | None:
        """
        顧客組織の主担当者を取得

        Args:
            client_organization_id: 顧客組織ID

        Returns:
            ClientContactEntity | None: 見つかった場合は主担当者エンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def update(self, client_contact: ClientContactEntity) -> ClientContactEntity:
        """
        顧客担当者情報を更新

        Args:
            client_contact: 更新する顧客担当者エンティティ

        Returns:
            ClientContactEntity: 更新された顧客担当者エンティティ

        Raises:
            ClientContactNotFoundError: 顧客担当者が見つからない場合
        """
        pass

    @abstractmethod
    async def soft_delete(self, client_contact_id: int) -> None:
        """
        顧客担当者を論理削除（ソフトデリート）

        Args:
            client_contact_id: 顧客担当者ID

        Raises:
            ClientContactNotFoundError: 顧客担当者が見つからない場合
        """
        pass
