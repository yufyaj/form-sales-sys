"""
送信禁止設定APIの結合テスト

実際のデータベースとHTTPクライアントを使用してAPIの動作を検証します。
IDOR対策、バリデーション、XSSサニタイゼーションのテストを含みます。
"""
from datetime import date, time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import Organization, List as ListModel, User, Role
from src.infrastructure.persistence.models.organization import OrganizationType
from src.app.core.security import hash_password


@pytest.fixture
async def test_organization_1(db_session: AsyncSession) -> Organization:
    """テスト用組織1を作成"""
    org = Organization(
        name="テスト組織1",
        type=OrganizationType.SALES_SUPPORT,
        email="org1@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_organization_2(db_session: AsyncSession) -> Organization:
    """テスト用組織2を作成（IDOR対策テスト用）"""
    org = Organization(
        name="テスト組織2",
        type=OrganizationType.SALES_SUPPORT,
        email="org2@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """テスト用ロールを作成"""
    role = Role(
        name="sales_support",
        display_name="営業支援会社",
        description="営業支援会社の担当者",
    )
    db_session.add(role)
    await db_session.flush()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_user_org1(
    db_session: AsyncSession, test_organization_1: Organization, test_role: Role
) -> User:
    """組織1のテストユーザーを作成"""
    user = User(
        organization_id=test_organization_1.id,
        email="user1@example.com",
        hashed_password=hash_password("password123"),
        full_name="テストユーザー1",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_org2(
    db_session: AsyncSession, test_organization_2: Organization, test_role: Role
) -> User:
    """組織2のテストユーザーを作成（IDOR対策テスト用）"""
    user = User(
        organization_id=test_organization_2.id,
        email="user2@example.com",
        hashed_password=hash_password("password123"),
        full_name="テストユーザー2",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_list_org1(
    db_session: AsyncSession, test_organization_1: Organization
) -> ListModel:
    """組織1のテストリストを作成"""
    list_model = ListModel(
        organization_id=test_organization_1.id,
        name="テストリスト1",
        description="組織1のリスト",
    )
    db_session.add(list_model)
    await db_session.flush()
    await db_session.refresh(list_model)
    return list_model


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """HTTPクライアント"""
    # 設定エラーを避けるため、ここでインポート
    from src.app.core.database import get_db
    from src.app.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers_org1(client: AsyncClient, test_user_org1: User) -> dict:
    """組織1ユーザーの認証ヘッダー"""
    response = await client.post(
        "/auth/login",
        json={
            "email": "user1@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_org2(client: AsyncClient, test_user_org2: User) -> dict:
    """組織2ユーザーの認証ヘッダー（IDOR対策テスト用）"""
    response = await client.post(
        "/auth/login",
        json={
            "email": "user2@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestNoSendSettingsCreate:
    """送信禁止設定作成APIのテスト"""

    async def test_create_day_of_week_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：曜日設定を作成できる"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "休日送信禁止",
                "description": "土日の送信を禁止",
                "is_enabled": True,
                "setting_type": "day_of_week",
                "day_of_week_list": [6, 7],
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "休日送信禁止"
        assert data["setting_type"] == "day_of_week"
        assert data["day_of_week_list"] == [6, 7]
        assert data["is_enabled"] is True
        assert "id" in data

    async def test_create_time_range_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：時間帯設定を作成できる"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/time-range?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "夜間送信禁止",
                "description": "22時から翌朝8時まで送信禁止",
                "is_enabled": True,
                "setting_type": "time_range",
                "time_start": "22:00:00",
                "time_end": "08:00:00",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "夜間送信禁止"
        assert data["setting_type"] == "time_range"
        assert data["time_start"] == "22:00:00"
        assert data["time_end"] == "08:00:00"

    async def test_create_specific_date_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：特定日付設定を作成できる"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/specific-date?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "元旦送信禁止",
                "description": "元旦の送信を禁止",
                "is_enabled": True,
                "setting_type": "specific_date",
                "specific_date": "2025-01-01",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "元旦送信禁止"
        assert data["setting_type"] == "specific_date"
        assert data["specific_date"] == "2025-01-01"

    async def test_create_date_range_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：日付範囲設定を作成できる"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/specific-date?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "年末年始送信禁止",
                "description": "年末年始の送信を禁止",
                "is_enabled": True,
                "setting_type": "specific_date",
                "date_range_start": "2025-12-29",
                "date_range_end": "2026-01-03",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "年末年始送信禁止"
        assert data["date_range_start"] == "2025-12-29"
        assert data["date_range_end"] == "2026-01-03"

    async def test_create_without_auth_returns_401(
        self,
        client: AsyncClient,
        test_list_org1: ListModel,
    ):
        """異常系：認証なしで401エラー"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            json={
                "name": "テスト",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )

        # Assert
        assert response.status_code == 401

    async def test_create_invalid_day_of_week_returns_422(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """異常系：不正な曜日値でバリデーションエラー"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "テスト",
                "setting_type": "day_of_week",
                "day_of_week_list": [8, 9],  # 不正な曜日
            },
        )

        # Assert
        assert response.status_code == 422

    async def test_create_xss_attempt_in_name_field_sanitized(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """セキュリティ：XSS攻撃のテキストがサニタイズされる"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "<script>alert('xss')</script>テスト",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        # 制御文字が除去されているはず
        assert "<script>" not in data["name"]
        assert "alert" in data["name"]  # printableな文字は残る

    async def test_create_date_range_too_long_returns_422(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """異常系：日付範囲が長すぎる場合バリデーションエラー"""
        # Act
        response = await client.post(
            f"/api/v1/no-send-settings/specific-date?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "長すぎる範囲",
                "setting_type": "specific_date",
                "date_range_start": "2025-01-01",
                "date_range_end": "2027-01-01",  # 2年間（長すぎる）
            },
        )

        # Assert
        assert response.status_code == 422


@pytest.mark.asyncio
class TestNoSendSettingsIDOR:
    """IDOR脆弱性対策のテスト"""

    async def test_get_setting_from_different_org_returns_404(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        auth_headers_org2: dict,
        test_list_org1: ListModel,
    ):
        """IDOR対策：異なる組織の設定取得時に404が返る"""
        # Arrange - 組織1のユーザーが設定を作成
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "組織1の設定",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )
        setting_id = create_response.json()["id"]

        # Act - 組織2のユーザーが組織1の設定にアクセス試行
        response = await client.get(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org2,
        )

        # Assert
        assert response.status_code == 404

    async def test_update_setting_from_different_org_returns_404(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        auth_headers_org2: dict,
        test_list_org1: ListModel,
    ):
        """IDOR対策：異なる組織の設定更新時に404が返る"""
        # Arrange
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "組織1の設定",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )
        setting_id = create_response.json()["id"]

        # Act - 組織2のユーザーが組織1の設定更新を試行
        response = await client.patch(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org2,
            json={"name": "不正な更新"},
        )

        # Assert
        assert response.status_code == 404

    async def test_delete_setting_from_different_org_returns_404(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        auth_headers_org2: dict,
        test_list_org1: ListModel,
    ):
        """IDOR対策：異なる組織の設定削除時に404が返る"""
        # Arrange
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "組織1の設定",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )
        setting_id = create_response.json()["id"]

        # Act - 組織2のユーザーが組織1の設定削除を試行
        response = await client.delete(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org2,
        )

        # Assert
        assert response.status_code == 404


@pytest.mark.asyncio
class TestNoSendSettingsCRUD:
    """送信禁止設定のCRUD操作テスト"""

    async def test_get_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：設定を取得できる"""
        # Arrange
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "テスト設定",
                "setting_type": "day_of_week",
                "day_of_week_list": [1, 2],
            },
        )
        setting_id = create_response.json()["id"]

        # Act
        response = await client.get(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org1,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == setting_id
        assert data["name"] == "テスト設定"

    async def test_list_settings_by_list_id(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：リストIDで設定一覧を取得できる"""
        # Arrange - 2つの設定を作成
        await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "設定1",
                "setting_type": "day_of_week",
                "day_of_week_list": [6],
            },
        )
        await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "設定2",
                "setting_type": "day_of_week",
                "day_of_week_list": [7],
            },
        )

        # Act
        response = await client.get(
            f"/api/v1/no-send-settings?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["settings"]) == 2

    async def test_update_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：設定を更新できる"""
        # Arrange
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "元の名前",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )
        setting_id = create_response.json()["id"]

        # Act
        response = await client.patch(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org1,
            json={
                "name": "更新後の名前",
                "is_enabled": False,
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新後の名前"
        assert data["is_enabled"] is False

    async def test_delete_setting_success(
        self,
        client: AsyncClient,
        auth_headers_org1: dict,
        test_list_org1: ListModel,
    ):
        """正常系：設定を削除（論理削除）できる"""
        # Arrange
        create_response = await client.post(
            f"/api/v1/no-send-settings/day-of-week?list_id={test_list_org1.id}",
            headers=auth_headers_org1,
            json={
                "name": "削除テスト",
                "setting_type": "day_of_week",
                "day_of_week_list": [1],
            },
        )
        setting_id = create_response.json()["id"]

        # Act
        response = await client.delete(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org1,
        )

        # Assert
        assert response.status_code == 204

        # 削除後は取得できない
        get_response = await client.get(
            f"/api/v1/no-send-settings/{setting_id}",
            headers=auth_headers_org1,
        )
        assert get_response.status_code == 404
