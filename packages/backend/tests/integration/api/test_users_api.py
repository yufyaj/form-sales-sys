"""
ユーザーAPI統合テスト

実際のデータベースを使用してAPIエンドポイントをテストします
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from infrastructure.persistence.models.organization import Organization
from infrastructure.persistence.models.role import Role


@pytest.mark.asyncio
async def test_create_user_success(db_session: AsyncSession, seed_roles: list[Role]) -> None:
    """ユーザー作成が成功することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # HTTPクライアントでAPIをテスト
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "full_name": "テストユーザー",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )

    # レスポンス検証
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "テストユーザー"
    assert data["organization_id"] == str(org.id)
    assert data["is_active"] is True
    assert data["is_email_verified"] is False


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    db_session: AsyncSession, seed_roles: list[Role]
) -> None:
    """重複したメールアドレスでユーザー作成が失敗することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # 1人目のユーザーを作成
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post(
            "/api/v1/users",
            json={
                "email": "duplicate@example.com",
                "full_name": "ユーザー1",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )

        # 同じメールアドレスで2人目を作成（失敗するはず）
        response = await client.post(
            "/api/v1/users",
            json={
                "email": "duplicate@example.com",
                "full_name": "ユーザー2",
                "password": "SecurePass456",
                "organization_id": str(org.id),
            },
        )

    # レスポンス検証
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "既に使用されています" in data["error"]["message"]


@pytest.mark.asyncio
async def test_get_user_success(db_session: AsyncSession, seed_roles: list[Role]) -> None:
    """ユーザー取得が成功することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # ユーザーを作成
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/users",
            json={
                "email": "gettest@example.com",
                "full_name": "取得テストユーザー",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )
        created_user = create_response.json()

        # ユーザーを取得
        response = await client.get(
            f"/api/v1/users/{created_user['id']}",
            params={"organization_id": str(org.id)},
        )

    # レスポンス検証
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_user["id"]
    assert data["email"] == "gettest@example.com"


@pytest.mark.asyncio
async def test_list_users_success(db_session: AsyncSession, seed_roles: list[Role]) -> None:
    """ユーザー一覧取得が成功することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # 複数のユーザーを作成
    async with AsyncClient(app=app, base_url="http://test") as client:
        for i in range(3):
            await client.post(
                "/api/v1/users",
                json={
                    "email": f"user{i}@example.com",
                    "full_name": f"ユーザー{i}",
                    "password": "SecurePass123",
                    "organization_id": str(org.id),
                },
            )

        # ユーザー一覧を取得
        response = await client.get(
            "/api/v1/users",
            params={"organization_id": str(org.id)},
        )

    # レスポンス検証
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["users"]) == 3


@pytest.mark.asyncio
async def test_update_user_success(db_session: AsyncSession, seed_roles: list[Role]) -> None:
    """ユーザー更新が成功することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # ユーザーを作成
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/users",
            json={
                "email": "updatetest@example.com",
                "full_name": "更新前",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )
        created_user = create_response.json()

        # ユーザーを更新
        response = await client.patch(
            f"/api/v1/users/{created_user['id']}",
            params={"organization_id": str(org.id)},
            json={"full_name": "更新後"},
        )

    # レスポンス検証
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "更新後"


@pytest.mark.asyncio
async def test_delete_inactive_user_success(
    db_session: AsyncSession, seed_roles: list[Role]
) -> None:
    """非アクティブなユーザー削除が成功することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # ユーザーを作成して非アクティブ化
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/users",
            json={
                "email": "deletetest@example.com",
                "full_name": "削除テスト",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )
        created_user = create_response.json()

        # 非アクティブ化
        await client.patch(
            f"/api/v1/users/{created_user['id']}",
            params={"organization_id": str(org.id)},
            json={"is_active": False},
        )

        # 削除
        response = await client.delete(
            f"/api/v1/users/{created_user['id']}",
            params={"organization_id": str(org.id)},
        )

    # レスポンス検証
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_active_user_fails(
    db_session: AsyncSession, seed_roles: list[Role]
) -> None:
    """アクティブなユーザー削除が失敗することをテスト"""
    # テスト用組織を作成
    org = Organization(name="テスト組織", description="統合テスト用")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # ユーザーを作成
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/v1/users",
            json={
                "email": "activedelete@example.com",
                "full_name": "アクティブ削除テスト",
                "password": "SecurePass123",
                "organization_id": str(org.id),
            },
        )
        created_user = create_response.json()

        # アクティブなまま削除しようとする（失敗するはず）
        response = await client.delete(
            f"/api/v1/users/{created_user['id']}",
            params={"organization_id": str(org.id)},
        )

    # レスポンス検証
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "アクティブなユーザーは削除できません" in data["error"]["message"]
