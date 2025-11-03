"""
認可機能の統合テスト

RoleCheckerとPermissionCheckerの動作を検証します。
実際のデータベースとFastAPIのテストクライアントを使用します。
"""
import pytest
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import (
    RoleChecker,
    PermissionChecker,
    get_current_user,
)
from src.app.core.security import create_access_token
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.role import Permission, Role
from src.infrastructure.persistence.models.user import User
from src.infrastructure.persistence.models.user_role import RolePermission, UserRole


@pytest.fixture
def test_app() -> FastAPI:
    """テスト用FastAPIアプリケーション"""
    app = FastAPI()

    @app.get("/test/admin-only")
    async def admin_only_endpoint(
        user: UserEntity = Depends(RoleChecker(["admin"]))
    ):
        return {"message": "Admin access granted", "user_id": user.id}

    @app.get("/test/client-or-worker")
    async def client_or_worker_endpoint(
        user: UserEntity = Depends(RoleChecker(["client", "worker"]))
    ):
        return {"message": "Client or worker access granted", "user_id": user.id}

    @app.get("/test/project-create")
    async def project_create_endpoint(
        user: UserEntity = Depends(PermissionChecker(["project:create"]))
    ):
        return {"message": "Project create permission granted", "user_id": user.id}

    @app.get("/test/project-read-or-update")
    async def project_read_or_update_endpoint(
        user: UserEntity = Depends(
            PermissionChecker(["project:read", "project:update"])
        )
    ):
        return {
            "message": "Project read or update permission granted",
            "user_id": user.id,
        }

    return app


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
async def admin_user(
    db_session: AsyncSession, test_organization: Organization
) -> tuple[User, str]:
    """管理者ユーザーとトークンを作成"""
    user = User(
        organization_id=test_organization.id,
        email="admin@example.com",
        hashed_password="$2b$12$hashedpassword",
        full_name="管理者ユーザー",
    )
    db_session.add(user)
    await db_session.flush()

    # adminロールを作成して割り当て
    admin_role = Role(name="admin", display_name="管理者", description="システム管理者")
    db_session.add(admin_role)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    await db_session.flush()

    # JWTトークンを生成
    token = create_access_token(data={"sub": str(user.id), "type": "access"})

    return user, token


@pytest.fixture
async def client_user(
    db_session: AsyncSession, test_organization: Organization
) -> tuple[User, str]:
    """顧客ユーザーとトークンを作成"""
    user = User(
        organization_id=test_organization.id,
        email="client@example.com",
        hashed_password="$2b$12$hashedpassword",
        full_name="顧客ユーザー",
    )
    db_session.add(user)
    await db_session.flush()

    # clientロールを作成して割り当て
    client_role = Role(name="client", display_name="顧客", description="顧客ユーザー")
    db_session.add(client_role)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role_id=client_role.id)
    db_session.add(user_role)
    await db_session.flush()

    # project:read権限を追加
    project_read = Permission(
        resource="project", action="read", description="プロジェクト読取権限"
    )
    db_session.add(project_read)
    await db_session.flush()

    role_perm = RolePermission(role_id=client_role.id, permission_id=project_read.id)
    db_session.add(role_perm)
    await db_session.flush()

    # JWTトークンを生成
    token = create_access_token(data={"sub": str(user.id), "type": "access"})

    return user, token


class TestRoleChecker:
    """RoleCheckerのテスト"""

    async def test_admin_only_endpoint_with_admin_user(
        self, test_app: FastAPI, admin_user: tuple[User, str]
    ) -> None:
        """正常系：管理者ユーザーが管理者限定エンドポイントにアクセスできる"""
        # Arrange
        _, token = admin_user
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/admin-only", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Admin access granted"

    async def test_admin_only_endpoint_with_client_user(
        self, test_app: FastAPI, client_user: tuple[User, str]
    ) -> None:
        """異常系：顧客ユーザーが管理者限定エンドポイントにアクセスできない"""
        # Arrange
        _, token = client_user
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/admin-only", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_client_or_worker_endpoint_with_client_user(
        self, test_app: FastAPI, client_user: tuple[User, str]
    ) -> None:
        """正常系：顧客ユーザーがclient or workerエンドポイントにアクセスできる"""
        # Arrange
        _, token = client_user
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/client-or-worker", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Client or worker access granted"

    async def test_endpoint_without_token(self, test_app: FastAPI) -> None:
        """異常系：トークンなしでアクセスできない"""
        # Arrange
        client = TestClient(test_app)

        # Act
        response = client.get("/test/admin-only")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPermissionChecker:
    """PermissionCheckerのテスト"""

    async def test_project_create_endpoint_with_permission(
        self,
        test_app: FastAPI,
        db_session: AsyncSession,
        client_user: tuple[User, str],
    ) -> None:
        """正常系：project:create権限を持つユーザーがアクセスできる"""
        # Arrange
        user, token = client_user

        # project:create権限を追加
        project_create = Permission(
            resource="project", action="create", description="プロジェクト作成権限"
        )
        db_session.add(project_create)
        await db_session.flush()

        # ユーザーのロールに権限を割り当て
        user_role = (
            await db_session.execute(
                f"SELECT role_id FROM user_roles WHERE user_id = {user.id}"
            )
        ).scalar_one()
        role_perm = RolePermission(role_id=user_role, permission_id=project_create.id)
        db_session.add(role_perm)
        await db_session.flush()

        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/project-create", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Project create permission granted"

    async def test_project_create_endpoint_without_permission(
        self, test_app: FastAPI, client_user: tuple[User, str]
    ) -> None:
        """異常系：project:create権限を持たないユーザーがアクセスできない"""
        # Arrange
        _, token = client_user
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/project-create", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_project_read_or_update_endpoint_with_read_permission(
        self, test_app: FastAPI, client_user: tuple[User, str]
    ) -> None:
        """正常系：project:read権限を持つユーザーがアクセスできる（OR条件）"""
        # Arrange
        # client_userはproject:read権限を持っている
        _, token = client_user
        client = TestClient(test_app)

        # Act
        response = client.get(
            "/test/project-read-or-update", headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.json()["message"] == "Project read or update permission granted"
        )
