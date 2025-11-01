"""
データベースモデルの統合テスト

実際のPostgreSQLコンテナを使用してモデルのCRUD操作をテストします。
TDDサイクルに従って、まずテストを書いてから実装を確認します。
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import (
    Organization,
    OrganizationType,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)


class TestOrganizationModel:
    """組織モデルのテスト"""

    @pytest.mark.asyncio
    async def test_create_sales_support_organization(self, db_session: AsyncSession) -> None:
        """営業支援会社の組織を作成できること"""
        # Arrange
        org = Organization(
            name="テスト営業支援株式会社",
            type=OrganizationType.SALES_SUPPORT,
            email="contact@test-sales.com",
            phone="03-1234-5678",
        )

        # Act
        db_session.add(org)
        await db_session.flush()
        await db_session.refresh(org)

        # Assert
        assert org.id is not None
        assert org.name == "テスト営業支援株式会社"
        assert org.type == OrganizationType.SALES_SUPPORT
        assert org.parent_organization_id is None
        assert org.created_at is not None
        assert org.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_client_organization_with_parent(self, db_session: AsyncSession) -> None:
        """顧客企業の組織を親組織（営業支援会社）付きで作成できること"""
        # Arrange
        sales_org = Organization(
            name="営業支援会社", type=OrganizationType.SALES_SUPPORT, email="sales@example.com"
        )
        db_session.add(sales_org)
        await db_session.flush()

        client_org = Organization(
            name="顧客企業",
            type=OrganizationType.CLIENT,
            parent_organization_id=sales_org.id,
            email="client@example.com",
        )

        # Act
        db_session.add(client_org)
        await db_session.flush()
        await db_session.refresh(client_org)

        # Assert
        assert client_org.id is not None
        assert client_org.type == OrganizationType.CLIENT
        assert client_org.parent_organization_id == sales_org.id

    @pytest.mark.asyncio
    async def test_soft_delete_organization(self, db_session: AsyncSession) -> None:
        """組織を論理削除できること"""
        # Arrange
        from datetime import datetime, timezone

        org = Organization(name="削除テスト組織", type=OrganizationType.SALES_SUPPORT)
        db_session.add(org)
        await db_session.flush()

        # Act
        org.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()
        await db_session.refresh(org)

        # Assert
        assert org.deleted_at is not None
        assert org.is_deleted is True


class TestUserModel:
    """ユーザーモデルのテスト"""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession) -> None:
        """ユーザーを作成できること"""
        # Arrange
        org = Organization(name="テスト組織", type=OrganizationType.SALES_SUPPORT)
        db_session.add(org)
        await db_session.flush()

        user = User(
            organization_id=org.id,
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="テスト太郎",
            phone="090-1234-5678",
            is_active=True,
        )

        # Act
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.organization_id == org.id
        assert user.is_active is True
        assert user.is_email_verified is False

    @pytest.mark.asyncio
    async def test_user_organization_relationship(self, db_session: AsyncSession) -> None:
        """ユーザーと組織のリレーションシップが正しく動作すること"""
        # Arrange
        org = Organization(name="リレーションテスト組織", type=OrganizationType.SALES_SUPPORT)
        db_session.add(org)
        await db_session.flush()

        user = User(
            organization_id=org.id,
            email="relation@example.com",
            hashed_password="password",
            full_name="リレーション太郎",
        )
        db_session.add(user)
        await db_session.flush()

        # Act
        result = await db_session.execute(
            select(User).where(User.id == user.id).options()
        )
        fetched_user = result.scalar_one()
        await db_session.refresh(fetched_user, ["organization"])

        # Assert
        assert fetched_user.organization.name == "リレーションテスト組織"


class TestRoleAndPermissionModel:
    """ロールと権限モデルのテスト"""

    @pytest.mark.asyncio
    async def test_create_role(self, db_session: AsyncSession) -> None:
        """ロールを作成できること"""
        # Arrange
        role = Role(name="test_role", display_name="テストロール", description="テスト用のロール")

        # Act
        db_session.add(role)
        await db_session.flush()
        await db_session.refresh(role)

        # Assert
        assert role.id is not None
        assert role.name == "test_role"
        assert role.display_name == "テストロール"

    @pytest.mark.asyncio
    async def test_create_permission(self, db_session: AsyncSession) -> None:
        """権限を作成できること"""
        # Arrange
        permission = Permission(
            resource="project", action="create", description="プロジェクトを作成する権限"
        )

        # Act
        db_session.add(permission)
        await db_session.flush()
        await db_session.refresh(permission)

        # Assert
        assert permission.id is not None
        assert permission.code == "project:create"

    @pytest.mark.asyncio
    async def test_assign_role_to_user(self, db_session: AsyncSession, seed_roles: list) -> None:
        """ユーザーにロールを割り当てられること"""
        # Arrange
        org = Organization(name="ロール割り当てテスト", type=OrganizationType.SALES_SUPPORT)
        db_session.add(org)
        await db_session.flush()

        user = User(
            organization_id=org.id,
            email="role@example.com",
            hashed_password="password",
            full_name="ロール太郎",
        )
        db_session.add(user)
        await db_session.flush()

        sales_support_role = seed_roles[0]  # 営業支援会社ロール

        # Act
        user_role = UserRole(user_id=user.id, role_id=sales_support_role.id)
        db_session.add(user_role)
        await db_session.flush()

        # Assert
        result = await db_session.execute(
            select(UserRole).where(UserRole.user_id == user.id)
        )
        fetched_user_role = result.scalar_one()
        assert fetched_user_role.role_id == sales_support_role.id

    @pytest.mark.asyncio
    async def test_assign_permission_to_role(self, db_session: AsyncSession, seed_roles: list) -> None:
        """ロールに権限を割り当てられること"""
        # Arrange
        role = seed_roles[0]  # 営業支援会社ロール
        permission = Permission(resource="project", action="create")
        db_session.add(permission)
        await db_session.flush()

        # Act
        role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
        db_session.add(role_permission)
        await db_session.flush()

        # Assert
        result = await db_session.execute(
            select(RolePermission).where(RolePermission.role_id == role.id)
        )
        fetched_role_permission = result.scalar_one()
        assert fetched_role_permission.permission_id == permission.id


class TestMultiTenancy:
    """マルチテナント機能のテスト"""

    @pytest.mark.asyncio
    async def test_users_isolated_by_organization(self, db_session: AsyncSession) -> None:
        """組織ごとにユーザーが分離されていること"""
        # Arrange
        org1 = Organization(name="組織1", type=OrganizationType.SALES_SUPPORT)
        org2 = Organization(name="組織2", type=OrganizationType.SALES_SUPPORT)
        db_session.add_all([org1, org2])
        await db_session.flush()

        user1 = User(
            organization_id=org1.id,
            email="user1@org1.com",
            hashed_password="password",
            full_name="組織1ユーザー",
        )
        user2 = User(
            organization_id=org2.id,
            email="user2@org2.com",
            hashed_password="password",
            full_name="組織2ユーザー",
        )
        db_session.add_all([user1, user2])
        await db_session.flush()

        # Act
        result = await db_session.execute(
            select(User).where(User.organization_id == org1.id)
        )
        org1_users = result.scalars().all()

        # Assert
        assert len(org1_users) == 1
        assert org1_users[0].email == "user1@org1.com"
