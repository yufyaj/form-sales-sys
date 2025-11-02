"""
認証APIの結合テスト

実際のデータベースとHTTPクライアントを使用してAPIの動作を検証します。
"""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.security import decode_access_token
from src.app.main import app
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType


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
    await db_session.commit()
    return org


@pytest.fixture
async def client() -> AsyncClient:
    """HTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestAuthRegister:
    """ユーザー登録APIのテスト"""

    async def test_register_success(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """正常系：ユーザーを登録できる"""
        # Act
        response = await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "新規ユーザー",
                "phone": "090-1234-5678",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "新規ユーザー"
        assert data["phone"] == "090-1234-5678"
        assert data["is_active"] is True
        assert data["is_email_verified"] is False
        assert "id" in data

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """異常系：重複メールアドレスでエラー"""
        # Arrange
        await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "duplicate@example.com",
                "password": "password123",
                "full_name": "ユーザー1",
            },
        )

        # Act
        response = await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "duplicate@example.com",
                "password": "password456",
                "full_name": "ユーザー2",
            },
        )

        # Assert
        assert response.status_code == 409

    async def test_register_invalid_password(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """異常系：無効なパスワードでエラー"""
        # Act - パスワードが短すぎる
        response = await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "test@example.com",
                "password": "short",
                "full_name": "テストユーザー",
            },
        )

        # Assert
        assert response.status_code == 422


class TestAuthLogin:
    """ログインAPIのテスト"""

    async def test_login_success(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """正常系：ログインできる"""
        # Arrange - ユーザーを登録
        await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "login@example.com",
                "password": "password123",
                "full_name": "ログインユーザー",
            },
        )

        # Act - ログイン
        response = await client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # トークンの検証
        token = data["access_token"]
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["email"] == "login@example.com"

    async def test_login_wrong_password(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """異常系：パスワードが間違っている"""
        # Arrange
        await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "user@example.com",
                "password": "correct_password",
                "full_name": "ユーザー",
            },
        )

        # Act
        response = await client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "wrong_password",
            },
        )

        # Assert
        assert response.status_code == 401

    async def test_login_user_not_found(self, client: AsyncClient) -> None:
        """異常系：ユーザーが見つからない"""
        # Act
        response = await client.post(
            "/auth/login",
            json={
                "email": "notfound@example.com",
                "password": "password123",
            },
        )

        # Assert
        assert response.status_code == 401


class TestAuthLogout:
    """ログアウトAPIのテスト"""

    async def test_logout(self, client: AsyncClient) -> None:
        """正常系：ログアウトできる"""
        # Act
        response = await client.post("/auth/logout")

        # Assert
        assert response.status_code == 204


class TestAuthPasswordReset:
    """パスワードリセットAPIのテスト"""

    async def test_password_reset_request(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """正常系：パスワードリセット依頼ができる"""
        # Arrange
        await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "reset@example.com",
                "password": "oldpassword123",
                "full_name": "リセットユーザー",
            },
        )

        # Act
        response = await client.post(
            "/auth/password-reset-request",
            json={"email": "reset@example.com"},
        )

        # Assert
        assert response.status_code == 204

    async def test_password_reset(
        self, client: AsyncClient, test_organization: Organization
    ) -> None:
        """正常系：パスワードをリセットできる"""
        # Arrange - ユーザーを登録
        register_response = await client.post(
            "/auth/register",
            json={
                "organization_id": test_organization.id,
                "email": "resettest@example.com",
                "password": "oldpassword123",
                "full_name": "リセットテストユーザー",
            },
        )
        user_id = register_response.json()["id"]

        # Act - パスワードをリセット
        response = await client.post(
            "/auth/password-reset",
            json={
                "token": str(user_id),  # Phase1では簡易実装
                "new_password": "newpassword456",
            },
        )

        # Assert
        assert response.status_code == 200

        # 新しいパスワードでログインできることを確認
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "resettest@example.com",
                "password": "newpassword456",
            },
        )
        assert login_response.status_code == 200
