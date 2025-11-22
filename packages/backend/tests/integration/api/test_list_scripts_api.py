"""
リストスクリプトAPI統合テスト

実際のデータベースを使用してAPIエンドポイントをテストします。
認証・認可のテストを含みます。
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.app.main import app
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.models.list import List, ListStatus
from src.infrastructure.persistence.models.organization import (
    Organization,
    OrganizationType,
)
from src.infrastructure.persistence.models.user import User


@pytest.fixture
async def auth_user_and_org(db_session: AsyncSession) -> tuple[User, Organization]:
    """認証済みユーザーと組織のフィクスチャ"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

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

    return auth_user, org


@pytest.fixture
async def test_list(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> List:
    """テスト用リストのフィクスチャ"""
    auth_user, org = auth_user_and_org

    test_list = List(
        organization_id=org.id,
        name="テストリスト",
        status=ListStatus.DRAFT,
    )
    db_session.add(test_list)
    await db_session.flush()

    return test_list


def create_user_entity(user: User) -> UserEntity:
    """UserモデルからUserEntityを作成するヘルパー"""
    return UserEntity(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
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


@pytest.mark.asyncio
async def test_create_script_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """スクリプト作成が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    # 依存性オーバーライド
    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "初回アプローチ用スクリプト",
                    "content": "お世話になっております。〇〇社の△△と申します。",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 201
        data = response.json()
        assert data["list_id"] == test_list.id
        assert data["title"] == "初回アプローチ用スクリプト"
        assert data["content"] == "お世話になっております。〇〇社の△△と申します。"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_script_unauthorized(db_session: AsyncSession) -> None:
    """認証なしの場合は401エラーを返すことをテスト"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    test_list = List(
        organization_id=org.id,
        name="テストリスト",
        status=ListStatus.DRAFT,
    )
    db_session.add(test_list)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "テスト",
                    "content": "テスト内容",
                },
                # 認証ヘッダーなし
            )

        # 401 Unauthorized を期待
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_script_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のリストでスクリプト作成すると404エラーを返すことをテスト（IDOR対策）"""
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

    # 組織Bのリスト
    list_b = List(
        organization_id=org_b.id,
        name="組織Bのリスト",
        status=ListStatus.DRAFT,
    )
    db_session.add(list_b)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user_a)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": list_b.id,  # 別組織のリストID
                    "title": "テスト",
                    "content": "テスト内容",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bのリストが見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_script_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """スクリプト取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # スクリプトを作成
            create_response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "テストスクリプト",
                    "content": "テスト内容です",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_script = create_response.json()

            # スクリプトを取得
            response = await client.get(
                f"/api/v1/list-scripts/{created_script['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_script["id"]
        assert data["title"] == "テストスクリプト"
        assert data["content"] == "テスト内容です"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_scripts_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """スクリプト一覧取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 複数のスクリプトを作成
            for i in range(3):
                await client.post(
                    "/api/v1/list-scripts",
                    json={
                        "list_id": test_list.id,
                        "title": f"スクリプト{i+1}",
                        "content": f"内容{i+1}",
                    },
                    headers={"Authorization": "Bearer mock_token"},
                )

            # スクリプト一覧を取得
            response = await client.get(
                f"/api/v1/list-scripts?list_id={test_list.id}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["scripts"]) == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_script_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """スクリプト更新が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # スクリプトを作成
            create_response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "初期タイトル",
                    "content": "初期内容",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_script = create_response.json()

            # スクリプトを更新
            response = await client.patch(
                f"/api/v1/list-scripts/{created_script['id']}",
                json={
                    "title": "更新後タイトル",
                    "content": "更新後内容",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新後タイトル"
        assert data["content"] == "更新後内容"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_script_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """スクリプト削除が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # スクリプトを作成
            create_response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "削除対象",
                    "content": "削除されます",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_script = create_response.json()

            # スクリプトを削除
            response = await client.delete(
                f"/api/v1/list-scripts/{created_script['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 204

        # 削除後に取得できないことを確認
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            get_response = await client.get(
                f"/api/v1/list-scripts/{created_script['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert get_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_script_validation_error(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    test_list: List,
) -> None:
    """バリデーションエラーのテスト"""
    auth_user, org = auth_user_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 空のタイトルでエラー
            response = await client.post(
                "/api/v1/list-scripts",
                json={
                    "list_id": test_list.id,
                    "title": "",  # 空のタイトルは不正
                    "content": "テスト内容",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 422 Unprocessable Entity を期待
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
