"""
ユーザーリポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.user_entity import UserEntity


class IUserRepository(ABC):
    """
    ユーザーリポジトリインターフェース

    ユーザーの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        organization_id: int,
        email: str,
        hashed_password: str,
        full_name: str,
        phone: str | None = None,
        avatar_url: str | None = None,
        description: str | None = None,
    ) -> UserEntity:
        """
        ユーザーを作成

        Args:
            organization_id: 所属組織ID
            email: メールアドレス
            hashed_password: ハッシュ化されたパスワード
            full_name: 氏名
            phone: 電話番号（オプション）
            avatar_url: プロフィール画像URL（オプション）
            description: 備考（オプション）

        Returns:
            UserEntity: 作成されたユーザーエンティティ

        Raises:
            DuplicateEmailError: メールアドレスが既に存在する場合
        """
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> UserEntity | None:
        """
        IDでユーザーを検索

        Args:
            user_id: ユーザーID

        Returns:
            UserEntity | None: 見つかった場合はユーザーエンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        """
        メールアドレスでユーザーを検索

        Args:
            email: メールアドレス

        Returns:
            UserEntity | None: 見つかった場合はユーザーエンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def update_password(self, user_id: int, hashed_password: str) -> UserEntity:
        """
        ユーザーのパスワードを更新

        Args:
            user_id: ユーザーID
            hashed_password: 新しいハッシュ化されたパスワード

        Returns:
            UserEntity: 更新されたユーザーエンティティ

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
        """
        pass

    @abstractmethod
    async def verify_email(self, user_id: int) -> UserEntity:
        """
        メールアドレスを認証済みにする

        Args:
            user_id: ユーザーID

        Returns:
            UserEntity: 更新されたユーザーエンティティ

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
        """
        pass
