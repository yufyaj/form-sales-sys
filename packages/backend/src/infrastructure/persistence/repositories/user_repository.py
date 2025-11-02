"""
ユーザーリポジトリの実装

SQLAlchemy 2.0の非同期APIを使用したユーザーリポジトリの実装
"""

from datetime import datetime, timezone
from typing import Sequence


from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import (
    CannotDeleteActiveUserException,
    DuplicateEmailException,
    UserNotFoundException,
)
from domain.interfaces.user_repository import IUserRepository
from infrastructure.persistence.models.user import User


class UserRepository(IUserRepository):
    """ユーザーリポジトリの実装クラス"""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: SQLAlchemyの非同期セッション
        """
        self._session = session

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
        try:
            self._session.add(user)
            await self._session.flush()
            await self._session.refresh(user)
            return user
        except IntegrityError as e:
            await self._session.rollback()
            # unique制約違反の場合はメールアドレス重複エラーとして扱う
            if "unique" in str(e).lower() and "email" in str(e).lower():
                raise DuplicateEmailException(user.email)
            raise

    async def find_by_id(self, user_id: int, organization_id: int) -> User | None:
        """
        IDでユーザーを検索（マルチテナント対応）

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（テナント分離）

        Returns:
            見つかったユーザー、存在しない場合はNone
        """
        stmt = select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == organization_id,
                User.deleted_at.is_(None),  # 論理削除されていないもののみ
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str, organization_id: int) -> User | None:
        """
        メールアドレスでユーザーを検索（マルチテナント対応）

        Args:
            email: メールアドレス
            organization_id: 組織ID（テナント分離）

        Returns:
            見つかったユーザー、存在しない場合はNone
        """
        stmt = select(User).where(
            and_(
                User.email == email,
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

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
        conditions = [User.organization_id == organization_id]

        if not include_deleted:
            conditions.append(User.deleted_at.is_(None))

        stmt = (
            select(User)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )

        result = await self._session.execute(stmt)
        return result.scalars().all()

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
        try:
            # 更新日時を設定
            user.updated_at = datetime.now(timezone.utc)

            await self._session.flush()
            await self._session.refresh(user)
            return user
        except IntegrityError as e:
            await self._session.rollback()
            if "unique" in str(e).lower() and "email" in str(e).lower():
                raise DuplicateEmailException(user.email)
            raise

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
        user = await self.find_by_id(user_id, organization_id)

        if user is None:
            raise UserNotFoundException(user_id=str(user_id))

        # アクティブなユーザーは削除できない（ビジネスルール）
        if user.is_active:
            raise CannotDeleteActiveUserException(user_id=str(user_id))

        # 論理削除
        user.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def exists_by_email(self, email: str, organization_id: int) -> bool:
        """
        メールアドレスの重複チェック

        Args:
            email: チェックするメールアドレス
            organization_id: 組織ID

        Returns:
            存在する場合True
        """
        stmt = select(User.id).where(
            and_(
                User.email == email,
                User.organization_id == organization_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

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
        conditions = [User.organization_id == organization_id]

        if not include_deleted:
            conditions.append(User.deleted_at.is_(None))

        stmt = select(func.count(User.id)).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one()
