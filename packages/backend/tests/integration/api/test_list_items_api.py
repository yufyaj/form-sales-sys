"""
リスト項目API統合テスト

実際のデータベースを使用してAPIエンドポイントをテストします。
認証・認可のテストを含みます。
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.app.main import app
from src.domain.entities.list_entity import ListStatus
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.list_item import ListItem
from src.infrastructure.persistence.models.organization import (
    Organization,
    OrganizationType,
)
from src.infrastructure.persistence.models.user import User


def create_user_entity(user: User) -> UserEntity:
    """UserモデルからUserEntityを作成するヘルパー"""
    return UserEntity(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        hashed_password=user.hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        description=user.description,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


@pytest.fixture
async def setup_test_data(
    db_session: AsyncSession,
) -> tuple[User, Organization, List, ListItem]:
    """テストデータのセットアップ"""
    # 組織作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    # 認証ユーザー作成
    auth_user = User(
        organization_id=org.id,
        email="authenticated@example.com",
        hashed_password="hashed_password",
        full_name="認証済みユーザー",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(auth_user)
    await db_session.flush()

    # リスト作成
    test_list = List(
        organization_id=org.id,
        name="テストリスト",
        description="テスト用のリスト",
        status=ListStatus.DRAFT,
    )
    db_session.add(test_list)
    await db_session.flush()

    # リスト項目作成
    list_item = ListItem(
        list_id=test_list.id,
        title="株式会社テスト",
        status="pending",
    )
    db_session.add(list_item)
    await db_session.flush()

    return auth_user, org, test_list, list_item


@pytest.mark.asyncio
async def test_update_list_item_success(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """リスト項目の更新が成功することをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # ステータスを更新
            response = await client.patch(
                f"/api/v1/list-items/{list_item.id}",
                json={
                    "status": "contacted",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == list_item.id
        assert data["title"] == "株式会社テスト"  # タイトルは変更されない
        assert data["status"] == "contacted"  # ステータスが更新される
        assert "created_at" in data
        assert "updated_at" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_status_success(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """リスト項目のステータス更新が成功することをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # ステータス専用エンドポイントでステータスを更新
            response = await client.patch(
                f"/api/v1/list-items/{list_item.id}/status",
                json={
                    "status": "negotiating",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == list_item.id
        assert data["title"] == "株式会社テスト"
        assert data["status"] == "negotiating"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_no_changes(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """変更なしでもリスト項目が返されることをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 何も変更しない
            response = await client.patch(
                f"/api/v1/list-items/{list_item.id}",
                json={},
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == list_item.id
        assert data["status"] == "pending"  # 変更なし
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_invalid_status(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """無効なステータス値でバリデーションエラーになることをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 無効なステータス値
            response = await client.patch(
                f"/api/v1/list-items/{list_item.id}",
                json={
                    "status": "invalid_status",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # バリデーションエラー
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_not_found(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """存在しないリスト項目IDで400エラーを返すことをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 存在しないリスト項目ID
            response = await client.patch(
                "/api/v1/list-items/99999",
                json={
                    "status": "contacted",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # Not Found
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のリスト項目は更新できないことをテスト（IDOR対策）"""
    # 組織A
    org_a = Organization(
        name="営業支援会社A",
        type=OrganizationType.SALES_SUPPORT,
        email="org_a@example.com",
    )
    db_session.add(org_a)
    await db_session.flush()

    # 組織B
    org_b = Organization(
        name="営業支援会社B",
        type=OrganizationType.SALES_SUPPORT,
        email="org_b@example.com",
    )
    db_session.add(org_b)
    await db_session.flush()

    # 組織Aの認証済みユーザー
    auth_user_a = User(
        organization_id=org_a.id,
        email="auth_user_a@example.com",
        hashed_password="hashed",
        full_name="認証ユーザーA",
        is_active=True,
    )
    db_session.add(auth_user_a)
    await db_session.flush()

    # 組織Bのリストとリスト項目
    list_b = List(
        organization_id=org_b.id,
        name="組織Bのリスト",
        description="テスト用",
        status=ListStatus.DRAFT,
    )
    db_session.add(list_b)
    await db_session.flush()

    list_item_b = ListItem(
        list_id=list_b.id,
        title="株式会社組織B",
        status="pending",
    )
    db_session.add(list_item_b)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user_a)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 組織Aのユーザーが組織Bのリスト項目を更新しようとする
            response = await client.patch(
                f"/api/v1/list-items/{list_item_b.id}",
                json={
                    "status": "contacted",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 400 Bad Request を期待（組織Aからは組織Bのリスト項目が見えない）
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_list_item_all_valid_statuses(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, ListItem],
) -> None:
    """すべての有効なステータス値で更新できることをテスト"""
    auth_user, org, test_list, list_item = setup_test_data

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # すべての有効なステータス値
    valid_statuses = [
        "pending",
        "contacted",
        "negotiating",
        "closed_won",
        "closed_lost",
        "on_hold",
    ]

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for status_value in valid_statuses:
                response = await client.patch(
                    f"/api/v1/list-items/{list_item.id}/status",
                    json={
                        "status": status_value,
                    },
                    headers={"Authorization": "Bearer mock_token"},
                )
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == status_value
    finally:
        app.dependency_overrides.clear()
