"""
セキュリティ機能の統合テスト

実装したセキュリティ機能が正常に動作することを検証します。
"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """HTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestSecurityHeaders:
    """セキュリティヘッダーのテスト"""

    async def test_security_headers_present(self, client: AsyncClient) -> None:
        """セキュリティヘッダーが設定されていることを確認"""
        # Act
        response = await client.get("/")

        # Assert
        headers = response.headers

        # 基本的なセキュリティヘッダーを確認
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in headers
        assert headers["x-xss-protection"] == "1; mode=block"

        assert "referrer-policy" in headers
        assert headers["referrer-policy"] == "strict-origin-when-cross-origin"

        # 開発環境ではHSTSとCSPは設定されない
        # 本番環境でのみ有効になることを期待


class TestJWTTokenMinimization:
    """JWTトークンの最小化テスト"""

    async def test_jwt_payload_minimal(self, client: AsyncClient) -> None:
        """JWTペイロードが最小限の情報のみを含むことを確認"""
        from jose import jwt as jose_jwt

        from src.app.core.config import get_settings

        settings = get_settings()

        # Arrange - テスト用トークンを生成
        from src.app.core.security import create_access_token

        token = create_access_token(data={"sub": "123", "type": "access"})

        # Act - トークンをデコード（検証なし）
        payload = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Assert - 必要最小限の情報のみを含む
        assert "sub" in payload  # ユーザーID
        assert "type" in payload  # トークンタイプ
        assert "exp" in payload  # 有効期限

        # 以下の情報は含まれていないこと（セキュリティ強化）
        assert "email" not in payload
        assert "organization_id" not in payload


class TestPasswordResetDisabled:
    """パスワードリセット機能が無効化されていることのテスト"""

    async def test_password_reset_request_disabled(self, client: AsyncClient) -> None:
        """パスワードリセット依頼が無効化されていることを確認"""
        # Act
        # レート制限があるため、時間をかけて実行
        import time

        response = await client.post(
            "/auth/password-reset-request", json={"email": "test@example.com"}
        )

        # タイミング攻撃対策により最低500msかかることを確認
        # （この時間はテストでは確認しない）

        # Assert
        assert response.status_code == 501  # Not Implemented
        assert "Phase 2" in response.json()["detail"]

    async def test_password_reset_disabled(self, client: AsyncClient) -> None:
        """パスワードリセットが無効化されていることを確認"""
        # Act
        response = await client.post(
            "/auth/password-reset", json={"token": "123", "new_password": "newpass123"}
        )

        # Assert
        assert response.status_code == 501  # Not Implemented
        assert "Phase 2" in response.json()["detail"]


class TestCORSConfiguration:
    """CORS設定のテスト"""

    async def test_cors_headers_present(self, client: AsyncClient) -> None:
        """CORSヘッダーが設定されていることを確認"""
        # Act - プリフライトリクエスト
        response = await client.options(
            "/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

        # Assert
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


class TestApplicationHealthCheck:
    """アプリケーションのヘルスチェック"""

    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """ルートエンドポイントが正常に動作することを確認"""
        # Act
        response = await client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    async def test_health_endpoint(self, client: AsyncClient) -> None:
        """ヘルスチェックエンドポイントが正常に動作することを確認"""
        # Act
        response = await client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
