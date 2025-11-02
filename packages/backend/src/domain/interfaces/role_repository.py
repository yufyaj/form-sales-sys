"""
ロールリポジトリの抽象インターフェース

ロール（営業支援会社、顧客、ワーカー）の管理を行うリポジトリインターフェース
"""

from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from infrastructure.persistence.models.role import Role


class IRoleRepository(ABC):
    """ロールリポジトリの抽象インターフェース"""

    @abstractmethod
    async def find_by_id(self, role_id: UUID) -> Role | None:
        """
        IDでロールを検索

        Args:
            role_id: ロールID

        Returns:
            見つかったロール、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        """
        名前でロールを検索

        Args:
            name: ロール名（例: sales_support, client, worker）

        Returns:
            見つかったロール、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def list_all(self) -> Sequence[Role]:
        """
        全ロール一覧を取得

        Returns:
            ロールのリスト
        """
        pass

    @abstractmethod
    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> None:
        """
        ユーザーにロールを割り当て

        Args:
            user_id: ユーザーID
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        pass

    @abstractmethod
    async def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> None:
        """
        ユーザーからロールを削除

        Args:
            user_id: ユーザーID
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        pass

    @abstractmethod
    async def get_user_roles(self, user_id: UUID) -> Sequence[Role]:
        """
        ユーザーに割り当てられたロール一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            ロールのリスト
        """
        pass

    @abstractmethod
    async def user_has_role(self, user_id: UUID, role_name: str) -> bool:
        """
        ユーザーが特定のロールを持っているか確認

        Args:
            user_id: ユーザーID
            role_name: ロール名

        Returns:
            ロールを持っている場合True
        """
        pass
