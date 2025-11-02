"""
ユーザーリポジトリの実装

IUserRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user_entity import UserEntity
from src.domain.exceptions import DuplicateEmailError, UserNotFoundError
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.persistence.models.user import User


class UserRepository(IUserRepository):
    """
    ユーザーリポジトリの実装

    SQLAlchemyを使用してユーザーの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

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
        """ユーザーを作成"""
        user = User(
            organization_id=organization_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            phone=phone,
            avatar_url=avatar_url,
            description=description,
        )

        self._session.add(user)

        try:
            await self._session.flush()
        except IntegrityError as e:
            # メールアドレスの重複エラーをキャッチ
            if "unique constraint" in str(e).lower() and "email" in str(e).lower():
                raise DuplicateEmailError(email)
            raise

        return self._to_entity(user)

    async def find_by_id(self, user_id: int) -> UserEntity | None:
        """IDでユーザーを検索"""
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return self._to_entity(user)

    async def find_by_email(self, email: str) -> UserEntity | None:
        """メールアドレスでユーザーを検索"""
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return self._to_entity(user)

    async def update_password(self, user_id: int, hashed_password: str) -> UserEntity:
        """ユーザーのパスワードを更新"""
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError(user_id=user_id)

        user.hashed_password = hashed_password
        await self._session.flush()
        await self._session.refresh(user)

        return self._to_entity(user)

    async def verify_email(self, user_id: int) -> UserEntity:
        """メールアドレスを認証済みにする"""
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError(user_id=user_id)

        user.is_email_verified = True
        await self._session.flush()
        await self._session.refresh(user)

        return self._to_entity(user)

    def _to_entity(self, user: User) -> UserEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return UserEntity(
            id=user.id,
            organization_id=user.organization_id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            description=user.description,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
