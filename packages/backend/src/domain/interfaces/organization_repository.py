"""
組織リポジトリの抽象インターフェース

営業支援会社組織と顧客組織の管理を行うリポジトリインターフェース
"""

from abc import ABC, abstractmethod
from typing import Sequence


from infrastructure.persistence.models.organization import Organization


class IOrganizationRepository(ABC):
    """組織リポジトリの抽象インターフェース"""

    @abstractmethod
    async def create(self, organization: Organization) -> Organization:
        """
        新規組織を作成

        Args:
            organization: 作成する組織エンティティ

        Returns:
            作成された組織
        """
        pass

    @abstractmethod
    async def find_by_id(self, organization_id: int) -> Organization | None:
        """
        IDで組織を検索

        Args:
            organization_id: 組織ID

        Returns:
            見つかった組織、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[Organization]:
        """
        全組織一覧を取得

        Args:
            skip: スキップする件数
            limit: 取得する最大件数
            include_deleted: 論理削除された組織を含むか

        Returns:
            組織のリスト
        """
        pass

    @abstractmethod
    async def list_by_parent(
        self,
        parent_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[Organization]:
        """
        親組織に紐づく子組織一覧を取得（顧客組織の取得）

        Args:
            parent_organization_id: 親組織ID
            skip: スキップする件数
            limit: 取得する最大件数
            include_deleted: 論理削除された組織を含むか

        Returns:
            子組織のリスト
        """
        pass

    @abstractmethod
    async def update(self, organization: Organization) -> Organization:
        """
        組織情報を更新

        Args:
            organization: 更新する組織エンティティ

        Returns:
            更新された組織

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
        """
        pass

    @abstractmethod
    async def soft_delete(self, organization_id: int) -> None:
        """
        組織を論理削除

        Args:
            organization_id: 組織ID

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
        """
        pass

    @abstractmethod
    async def count_all(self, include_deleted: bool = False) -> int:
        """
        組織の総数を取得

        Args:
            include_deleted: 論理削除された組織を含むか

        Returns:
            組織数
        """
        pass
