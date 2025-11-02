"""
ユーザーリポジトリの抽象インターフェース

依存性逆転の原則（DIP）に基づき、ドメイン層でインターフェースを定義し、
インフラ層で実装します。これにより、ビジネスロジックをDBの実装詳細から分離します。
"""

from abc import ABC, abstractmethod
from typing import Sequence


from infrastructure.persistence.models.user import User


class IUserRepository(ABC):
    """ユーザーリポジトリの抽象インターフェース"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        新規ユーザーを作成

        Args:
            user: 作成するユーザーエンティティ

        Returns:
            作成されたユーザー

        Raises:
            DuplicateEmailException: メールアドレスが重複している場合
        """
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int, organization_id: int) -> User | None:
        """
        IDでユーザーを検索（マルチテナント対応）

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（テナント分離）

        Returns:
            見つかったユーザー、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str, organization_id: int) -> User | None:
        """
        メールアドレスでユーザーを検索（マルチテナント対応）

        Args:
            email: メールアドレス
            organization_id: 組織ID（テナント分離）

        Returns:
            見つかったユーザー、存在しない場合はNone
        """
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[User]:
        """
        組織に所属するユーザー一覧を取得

        Args:
            organization_id: 組織ID
            skip: スキップする件数（ページネーション）
            limit: 取得する最大件数
            include_deleted: 論理削除されたユーザーを含むか

        Returns:
            ユーザーのリスト
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        ユーザー情報を更新

        Args:
            user: 更新するユーザーエンティティ

        Returns:
            更新されたユーザー

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            DuplicateEmailException: メールアドレスが重複している場合
        """
        pass

    @abstractmethod
    async def soft_delete(self, user_id: int, organization_id: int) -> None:
        """
        ユーザーを論理削除

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（テナント分離）

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            CannotDeleteActiveUserException: アクティブなユーザーを削除しようとした場合
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str, organization_id: int) -> bool:
        """
        メールアドレスの重複チェック

        Args:
            email: チェックするメールアドレス
            organization_id: 組織ID

        Returns:
            存在する場合True
        """
        pass

    @abstractmethod
    async def count_by_organization(
        self, organization_id: int, include_deleted: bool = False
    ) -> int:
        """
        組織に所属するユーザー数を取得

        Args:
            organization_id: 組織ID
            include_deleted: 論理削除されたユーザーを含むか

        Returns:
            ユーザー数
        """
        pass
