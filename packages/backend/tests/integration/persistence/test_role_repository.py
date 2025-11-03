"""
ロールリポジトリの結合テスト

実際のデータベースを使用してRoleRepositoryの動作を検証します。
特に認可機能（RBAC）のテストに焦点を当てます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.role import Permission, Role
from src.infrastructure.persistence.models.user import User
from src.infrastructure.persistence.models.user_role import RolePermission, UserRole
from src.infrastructure.persistence.repositories.role_repository import RoleRepository


@pytest.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """テスト用組織を作成"""
    org = Organization(
        name="テスト組織",
        type=OrganizationType.CLIENT,
        email="test@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """テスト用ユーザーを作成"""
    user = User(
        organization_id=test_organization.id,
        email="testuser@example.com",
        hashed_password="$2b$12$hashedpassword",
        full_name="テストユーザー",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_roles(db_session: AsyncSession) -> dict[str, Role]:
    """テスト用ロールを作成"""
    admin_role = Role(name="admin", display_name="管理者", description="システム管理者")
    client_role = Role(name="client", display_name="顧客", description="顧客ユーザー")
    worker_role = Role(name="worker", display_name="ワーカー", description="ワーカー")

    db_session.add(admin_role)
    db_session.add(client_role)
    db_session.add(worker_role)
    await db_session.flush()

    return {
        "admin": admin_role,
        "client": client_role,
        "worker": worker_role,
    }


@pytest.fixture
async def test_permissions(db_session: AsyncSession) -> dict[str, Permission]:
    """テスト用権限を作成"""
    project_create = Permission(
        resource="project", action="create", description="プロジェクト作成権限"
    )
    project_read = Permission(
        resource="project", action="read", description="プロジェクト読取権限"
    )
    project_update = Permission(
        resource="project", action="update", description="プロジェクト更新権限"
    )
    project_delete = Permission(
        resource="project", action="delete", description="プロジェクト削除権限"
    )

    db_session.add(project_create)
    db_session.add(project_read)
    db_session.add(project_update)
    db_session.add(project_delete)
    await db_session.flush()

    return {
        "project:create": project_create,
        "project:read": project_read,
        "project:update": project_update,
        "project:delete": project_delete,
    }


class TestRoleRepositoryUserHasAnyRole:
    """user_has_any_roleメソッドのテスト"""

    async def test_user_has_any_role_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
    ) -> None:
        """正常系：ユーザーが指定されたロールのいずれかを持っている"""
        # Arrange
        repo = RoleRepository(db_session)
        # ユーザーにclientロールを割り当て
        user_role = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        db_session.add(user_role)
        await db_session.flush()

        # Act
        has_role = await repo.user_has_any_role(
            test_user.id, ["admin", "client", "worker"]
        )

        # Assert
        assert has_role is True

    async def test_user_has_any_role_not_found(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
    ) -> None:
        """正常系：ユーザーが指定されたロールのいずれも持っていない"""
        # Arrange
        repo = RoleRepository(db_session)

        # Act
        has_role = await repo.user_has_any_role(test_user.id, ["admin", "worker"])

        # Assert
        assert has_role is False

    async def test_user_has_any_role_empty_list(
        self,
        db_session: AsyncSession,
        test_user: User,
    ) -> None:
        """境界値：空のロールリストでFalseを返す"""
        # Arrange
        repo = RoleRepository(db_session)

        # Act
        has_role = await repo.user_has_any_role(test_user.id, [])

        # Assert
        assert has_role is False


class TestRoleRepositoryGetUserPermissions:
    """get_user_permissionsメソッドのテスト"""

    async def test_get_user_permissions_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
        test_permissions: dict[str, Permission],
    ) -> None:
        """正常系：ユーザーの権限を取得できる"""
        # Arrange
        repo = RoleRepository(db_session)

        # ユーザーにclientロールを割り当て
        user_role = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        db_session.add(user_role)
        await db_session.flush()

        # clientロールにproject:readとproject:createの権限を割り当て
        role_perm1 = RolePermission(
            role_id=test_roles["client"].id,
            permission_id=test_permissions["project:read"].id,
        )
        role_perm2 = RolePermission(
            role_id=test_roles["client"].id,
            permission_id=test_permissions["project:create"].id,
        )
        db_session.add(role_perm1)
        db_session.add(role_perm2)
        await db_session.flush()

        # Act
        permissions = await repo.get_user_permissions(test_user.id)

        # Assert
        assert len(permissions) == 2
        assert "project:read" in permissions
        assert "project:create" in permissions

    async def test_get_user_permissions_multiple_roles(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
        test_permissions: dict[str, Permission],
    ) -> None:
        """正常系：複数のロールからの権限を統合して取得できる"""
        # Arrange
        repo = RoleRepository(db_session)

        # ユーザーにclientとworkerロールを割り当て
        user_role1 = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        user_role2 = UserRole(user_id=test_user.id, role_id=test_roles["worker"].id)
        db_session.add(user_role1)
        db_session.add(user_role2)
        await db_session.flush()

        # clientロールにproject:readを割り当て
        role_perm1 = RolePermission(
            role_id=test_roles["client"].id,
            permission_id=test_permissions["project:read"].id,
        )
        # workerロールにproject:createを割り当て
        role_perm2 = RolePermission(
            role_id=test_roles["worker"].id,
            permission_id=test_permissions["project:create"].id,
        )
        db_session.add(role_perm1)
        db_session.add(role_perm2)
        await db_session.flush()

        # Act
        permissions = await repo.get_user_permissions(test_user.id)

        # Assert
        assert len(permissions) == 2
        assert "project:read" in permissions
        assert "project:create" in permissions

    async def test_get_user_permissions_no_permissions(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
    ) -> None:
        """正常系：権限がない場合は空リストを返す"""
        # Arrange
        repo = RoleRepository(db_session)

        # ユーザーにclientロールを割り当てるが、権限は割り当てない
        user_role = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        db_session.add(user_role)
        await db_session.flush()

        # Act
        permissions = await repo.get_user_permissions(test_user.id)

        # Assert
        assert len(permissions) == 0


class TestRoleRepositoryUserHasPermission:
    """user_has_permissionメソッドのテスト"""

    async def test_user_has_permission_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
        test_permissions: dict[str, Permission],
    ) -> None:
        """正常系：ユーザーが指定された権限を持っている"""
        # Arrange
        repo = RoleRepository(db_session)

        # ユーザーにclientロールを割り当て
        user_role = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        db_session.add(user_role)
        await db_session.flush()

        # clientロールにproject:readの権限を割り当て
        role_perm = RolePermission(
            role_id=test_roles["client"].id,
            permission_id=test_permissions["project:read"].id,
        )
        db_session.add(role_perm)
        await db_session.flush()

        # Act
        has_permission = await repo.user_has_permission(test_user.id, "project:read")

        # Assert
        assert has_permission is True

    async def test_user_has_permission_not_found(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_roles: dict[str, Role],
    ) -> None:
        """正常系：ユーザーが指定された権限を持っていない"""
        # Arrange
        repo = RoleRepository(db_session)

        # ユーザーにclientロールを割り当てるが、権限は割り当てない
        user_role = UserRole(user_id=test_user.id, role_id=test_roles["client"].id)
        db_session.add(user_role)
        await db_session.flush()

        # Act
        has_permission = await repo.user_has_permission(test_user.id, "project:create")

        # Assert
        assert has_permission is False

    async def test_user_has_permission_invalid_format(
        self,
        db_session: AsyncSession,
        test_user: User,
    ) -> None:
        """異常系：無効な権限コード形式でFalseを返す"""
        # Arrange
        repo = RoleRepository(db_session)

        # Act
        has_permission = await repo.user_has_permission(test_user.id, "invalid_format")

        # Assert
        assert has_permission is False
