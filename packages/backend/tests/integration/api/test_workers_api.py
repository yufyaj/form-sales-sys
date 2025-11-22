"""
ワーカーAPI統合テスト（認証対応版）

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
from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus


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
async def test_create_worker_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ワーカー作成が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    # テスト用ユーザーを作成（ワーカー情報を付与する対象）
    user = User(
        organization_id=org.id,
        email="worker@example.com",
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
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "pending",
                    "skill_level": "intermediate",
                    "experience_months": 12,
                    "specialties": "BtoB営業、IT業界",
                    "max_tasks_per_day": 10,
                    "available_hours_per_week": 40,
                    "notes": "テストワーカー",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user.id
        assert data["organization_id"] == org.id
        assert data["status"] == "pending"
        assert data["skill_level"] == "intermediate"
        assert data["experience_months"] == 12
        assert data["specialties"] == "BtoB営業、IT業界"
        assert data["max_tasks_per_day"] == 10
        assert data["available_hours_per_week"] == 40
        assert data["notes"] == "テストワーカー"
        assert data["completed_tasks_count"] == 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_worker_unauthorized(db_session: AsyncSession) -> None:
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
        email="worker@example.com",
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
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "pending",
                },
                # 認証ヘッダーなし
            )

        # 401 Unauthorized を期待
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_worker_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のユーザーでワーカー作成すると404エラーを返すことをテスト（IDOR対策）"""
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

    # 組織Bのユーザー（これにワーカー情報を追加しようとする）
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
                "/api/v1/workers",
                json={
                    "user_id": user_b.id,  # 別組織のユーザーID
                    "status": "pending",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bのユーザーが見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_worker_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ワーカー取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="worker2@example.com",
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
            # ワーカーを作成
            create_response = await client.post(
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "active",
                    "skill_level": "advanced",
                    "experience_months": 24,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_worker = create_response.json()

            # ワーカーを取得
            response = await client.get(
                f"/api/v1/workers/{created_worker['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_worker["id"]
        assert data["status"] == "active"
        assert data["skill_level"] == "advanced"
        assert data["experience_months"] == 24
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_worker_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のワーカー取得は404エラーを返すことをテスト（IDOR対策）"""
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

    # 組織Bのユーザーとワーカー
    user_b = User(
        organization_id=org_b.id,
        email="user_b@example.com",
        hashed_password="hashed",
        full_name="ユーザーB",
        is_active=True,
    )
    db_session.add(user_b)
    await db_session.flush()

    # 組織Bの認証ユーザーでワーカーを作成
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

    # 組織Bでワーカーを作成
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/v1/workers",
            json={
                "user_id": user_b.id,
                "status": "active",
            },
            headers={"Authorization": "Bearer mock_token"},
        )
        created_worker = create_response.json()

    # 組織Aのユーザーで組織Bのワーカーを取得しようとする
    async def override_get_current_active_user_a():
        return create_user_entity(auth_user_a)

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user_a

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/workers/{created_worker['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bのワーカーが見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_workers_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ワーカー一覧取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    # 複数のユーザーとワーカーを作成
    for i in range(3):
        user = User(
            organization_id=org.id,
            email=f"worker{i+10}@example.com",
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
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "active" if i % 2 == 0 else "pending",
                    "skill_level": "intermediate",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # ワーカー一覧を取得
            response = await client.get(
                "/api/v1/workers",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["workers"]) == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_workers_with_status_filter(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ステータスフィルタ付きワーカー一覧取得をテスト"""
    auth_user, org = auth_user_and_org

    # 複数のワーカーを作成（異なるステータス）
    statuses = ["active", "pending", "active"]
    for i, status in enumerate(statuses):
        user = User(
            organization_id=org.id,
            email=f"worker_filter{i+20}@example.com",
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
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": status,
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # activeステータスのワーカーのみ取得
            response = await client.get(
                "/api/v1/workers?status=active",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # activeは2件
        assert len(data["workers"]) == 2
        for worker in data["workers"]:
            assert worker["status"] == "active"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_worker_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ワーカー更新が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="worker3@example.com",
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
            # ワーカーを作成
            create_response = await client.post(
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "pending",
                    "skill_level": "beginner",
                    "experience_months": 6,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_worker = create_response.json()

            # ワーカーを更新
            response = await client.patch(
                f"/api/v1/workers/{created_worker['id']}",
                json={
                    "status": "active",
                    "skill_level": "intermediate",
                    "experience_months": 12,
                    "completed_tasks_count": 50,
                    "success_rate": 85.5,
                    "rating": 4.5,
                    "notes": "パフォーマンス向上",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["skill_level"] == "intermediate"
        assert data["experience_months"] == 12
        assert data["completed_tasks_count"] == 50
        assert data["success_rate"] == 85.5
        assert data["rating"] == 4.5
        assert data["notes"] == "パフォーマンス向上"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_worker_success_with_auth(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """ワーカー削除が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="worker4@example.com",
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
            # ワーカーを作成
            create_response = await client.post(
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "active",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_worker = create_response.json()

            # ワーカーを削除
            response = await client.delete(
                f"/api/v1/workers/{created_worker['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 204

        # 削除後に取得できないことを確認
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            get_response = await client.get(
                f"/api/v1/workers/{created_worker['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert get_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_worker_validation_error(
    db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]
) -> None:
    """バリデーションエラーのテスト"""
    auth_user, org = auth_user_and_org

    user = User(
        organization_id=org.id,
        email="worker5@example.com",
        hashed_password="hashed_password",
        full_name="テストユーザー",
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
            # 負の経験月数でエラー
            response = await client.post(
                "/api/v1/workers",
                json={
                    "user_id": user.id,
                    "status": "pending",
                    "experience_months": -1,  # 負の値は不正
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 422 Unprocessable Entity を期待
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
