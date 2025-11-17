"""
営業支援会社担当者API統合テスト（認証対応版）

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
async def test_create_staff_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """営業支援会社担当者作成が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    # テスト用ユーザーを作成（担当者情報を付与する対象）
    user = User(
        organization_id=org.id,
        email="staff@example.com",
        hashed_password="hashed_password",
        full_name="山田太郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

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
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": "営業部",
                    "position": "課長",
                    "employee_number": "EMP-001",
                    "notes": "テスト担当者",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user.id
        assert data["organization_id"] == org.id
        assert data["department"] == "営業部"
        assert data["position"] == "課長"
        assert data["employee_number"] == "EMP-001"
        assert data["notes"] == "テスト担当者"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_staff_unauthorized(db_session: AsyncSession) -> None:
    """認証なしの場合は401エラーを返すことをテスト"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    user = User(
        organization_id=org.id,
        email="staff@example.com",
        hashed_password="hashed_password",
        full_name="山田太郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": "営業部",
                },
                # 認証ヘッダーなし
            )

        # 401 Unauthorized を期待
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_staff_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のユーザーで担当者作成すると404エラーを返すことをテスト（IDOR対策）"""
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
    auth_user = User(
        organization_id=org_a.id,
        email="auth_user_a@example.com",
        hashed_password="hashed",
        full_name="認証ユーザーA",
        is_active=True,
    )
    db_session.add(auth_user)
    await db_session.flush()

    # 組織Bのユーザー（これに担当者情報を追加しようとする）
    user_b = User(
        organization_id=org_b.id,
        email="user_b@example.com",
        hashed_password="hashed",
        full_name="ユーザーB",
        is_active=True,
    )
    db_session.add(user_b)
    await db_session.flush()

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
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user_b.id,  # 別組織のユーザーID
                    "department": "営業部",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bのユーザーが見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_staff_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """営業支援会社担当者取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="staff2@example.com",
        hashed_password="hashed_password",
        full_name="佐藤花子",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

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
            # 担当者を作成
            create_response = await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": "総務部",
                    "position": "主任",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_staff = create_response.json()

            # 担当者を取得
            response = await client.get(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_staff["id"]
        assert data["department"] == "総務部"
        assert data["position"] == "主任"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_staff_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織の担当者取得は404エラーを返すことをテスト（IDOR対策）"""
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
        email="auth_a@example.com",
        hashed_password="hashed",
        full_name="認証ユーザーA",
        is_active=True,
    )
    db_session.add(auth_user_a)
    await db_session.flush()

    # 組織Bのユーザーと担当者
    user_b = User(
        organization_id=org_b.id,
        email="user_b@example.com",
        hashed_password="hashed",
        full_name="ユーザーB",
        is_active=True,
    )
    db_session.add(user_b)
    await db_session.flush()

    # 組織Bの認証ユーザーで担当者を作成
    auth_user_b = User(
        organization_id=org_b.id,
        email="auth_b@example.com",
        hashed_password="hashed",
        full_name="認証ユーザーB",
        is_active=True,
    )
    db_session.add(auth_user_b)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user_b():
        return create_user_entity(auth_user_b)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user_b

    # 組織Bで担当者を作成
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/v1/sales-company-staff",
            json={
                "user_id": user_b.id,
                "department": "営業部",
            },
            headers={"Authorization": "Bearer mock_token"},
        )
        created_staff = create_response.json()

    # 組織Aのユーザーで組織Bの担当者を取得しようとする
    async def override_get_current_active_user_a():
        return create_user_entity(auth_user_a)

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user_a

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bの担当者が見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_staff_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """営業支援会社担当者一覧取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    # 複数のユーザーと担当者を作成
    for i in range(3):
        user = User(
            organization_id=org.id,
            email=f"staff{i+10}@example.com",
            hashed_password="hashed_password",
            full_name=f"テスト{i+1}",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        async def override_get_db():
            yield db_session

        async def override_get_current_active_user():
            return create_user_entity(auth_user)

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = override_get_current_active_user

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": f"部署{i+1}",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 担当者一覧を取得
            response = await client.get(
                "/api/v1/sales-company-staff",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["staff"]) == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_staff_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """営業支援会社担当者更新が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="staff3@example.com",
        hashed_password="hashed_password",
        full_name="鈴木一郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

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
            # 担当者を作成
            create_response = await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": "営業部",
                    "position": "主任",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_staff = create_response.json()

            # 担当者を更新
            response = await client.patch(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
                json={"position": "課長", "notes": "昇進"},
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == "課長"
        assert data["notes"] == "昇進"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_staff_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """営業支援会社担当者削除が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="staff4@example.com",
        hashed_password="hashed_password",
        full_name="田中次郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

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
            # 担当者を作成
            create_response = await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": "営業部",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_staff = create_response.json()

            # 担当者を削除
            response = await client.delete(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()
