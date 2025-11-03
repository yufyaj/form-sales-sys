"""
ロールリポジトリの実装

ロール（営業支援会社、顧客、ワーカー）の管理を行うリポジトリ実装
"""

from typing import Sequence


from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.exceptions import RoleNotFoundException, UserNotFoundException
from src.domain.interfaces.role_repository import IRoleRepository
from src.infrastructure.persistence.models.role import Permission, Role
from src.infrastructure.persistence.models.user import User
from src.infrastructure.persistence.models.user_role import RolePermission, UserRole


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

    async def user_has_any_role(self, user_id: int, role_names: list[str]) -> bool:
        """
        ユーザーが指定されたロールのいずれかを持っているか確認

        Args:
            user_id: ユーザーID
            role_names: ロール名のリスト

        Returns:
            いずれかのロールを持っている場合True
        """
        if not role_names:
            return False

        stmt = (
            select(UserRole.id)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Role.name.in_(role_names),
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_permissions(self, user_id: int) -> Sequence[str]:
        """
        ユーザーが持つ全ての権限コードを取得

        Args:
            user_id: ユーザーID

        Returns:
            権限コードのリスト（例: ["project:create", "project:read"]）
        """
        stmt = (
            select(Permission.resource, Permission.action)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, RolePermission.role_id == Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await self._session.execute(stmt)
        permissions = result.all()

        # resource:action形式の権限コードに変換
        return [f"{perm.resource}:{perm.action}" for perm in permissions]

    async def user_has_permission(self, user_id: int, permission_code: str) -> bool:
        """
        ユーザーが特定の権限を持っているか確認

        Args:
            user_id: ユーザーID
            permission_code: 権限コード（例: "project:create"）

        Returns:
            権限を持っている場合True
        """
        # 権限コードをリソースとアクションに分割
        try:
            resource, action = permission_code.split(":", 1)
        except ValueError:
            # 無効な権限コード形式
            return False

        stmt = (
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, RolePermission.role_id == Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Permission.resource == resource,
                    Permission.action == action,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
