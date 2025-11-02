"""
ロールリポジトリの実装

ロール（営業支援会社、顧客、ワーカー）の管理を行うリポジトリ実装
"""

from typing import Sequence


from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.exceptions import RoleNotFoundException, UserNotFoundException
from domain.interfaces.role_repository import IRoleRepository
from infrastructure.persistence.models.role import Role
from infrastructure.persistence.models.user import User
from infrastructure.persistence.models.user_role import UserRole


class RoleRepository(IRoleRepository):
    """ロールリポジトリの実装クラス"""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: SQLAlchemyの非同期セッション
        """
        self._session = session

    async def find_by_id(self, role_id: int) -> Role | None:
        """
        IDでロールを検索

        Args:
            role_id: ロールID

        Returns:
            見つかったロール、存在しない場合はNone
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Role | None:
        """
        名前でロールを検索

        Args:
            name: ロール名（例: sales_support, client, worker）

        Returns:
            見つかったロール、存在しない場合はNone
        """
        stmt = select(Role).where(Role.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Role]:
        """
        全ロール一覧を取得

        Returns:
            ロールのリスト
        """
        stmt = select(Role).order_by(Role.name)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def assign_role_to_user(self, user_id: int, role_id: int) -> None:
        """
        ユーザーにロールを割り当て

        Args:
            user_id: ユーザーID
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        # ユーザーの存在確認
        user_stmt = select(User.id).where(User.id == user_id)
        user_result = await self._session.execute(user_stmt)
        if user_result.scalar_one_or_none() is None:
            raise UserNotFoundException(user_id=str(user_id))

        # ロールの存在確認
        role_stmt = select(Role.id).where(Role.id == role_id)
        role_result = await self._session.execute(role_stmt)
        if role_result.scalar_one_or_none() is None:
            raise RoleNotFoundException(role_id=str(role_id))

        # 既に割り当てられているかチェック
        existing_stmt = select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        existing_result = await self._session.execute(existing_stmt)
        if existing_result.scalar_one_or_none() is not None:
            # 既に割り当てられている場合は何もしない
            return

        # ロールを割り当て
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self._session.add(user_role)
        await self._session.flush()

    async def remove_role_from_user(self, user_id: int, role_id: int) -> None:
        """
        ユーザーからロールを削除

        Args:
            user_id: ユーザーID
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        # 割り当てを検索
        stmt = select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        result = await self._session.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role is not None:
            await self._session.delete(user_role)
            await self._session.flush()

    async def get_user_roles(self, user_id: int) -> Sequence[Role]:
        """
        ユーザーに割り当てられたロール一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            ロールのリスト
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.name)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def user_has_role(self, user_id: int, role_name: str) -> bool:
        """
        ユーザーが特定のロールを持っているか確認

        Args:
            user_id: ユーザーID
            role_name: ロール名

        Returns:
            ロールを持っている場合True
        """
        stmt = (
            select(UserRole.id)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Role.name == role_name,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
