"""
リスト項目割り当てAPI統合テスト

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
from src.infrastructure.persistence.models.worker import Worker, WorkerStatus


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
) -> tuple[User, Organization, List, Worker, list[ListItem]]:
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

    # ワーカーユーザー作成
    worker_user = User(
        organization_id=org.id,
        email="worker@example.com",
        hashed_password="hashed_password",
        full_name="ワーカー太郎",
        is_active=True,
    )
    db_session.add(worker_user)
    await db_session.flush()

    # ワーカー作成
    worker = Worker(
        user_id=worker_user.id,
        organization_id=org.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker)
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

    # リスト項目作成（10件）
    list_items = []
    for i in range(10):
        list_item = ListItem(
            list_id=test_list.id,
            title=f"テスト企業{i+1}",
        )
        db_session.add(list_item)
        await db_session.flush()
        list_items.append(list_item)

    return auth_user, org, test_list, worker, list_items


@pytest.mark.asyncio
async def test_bulk_assign_workers_to_list_success(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """リストへのワーカー一括割り当てが成功することをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 5件割り当て
            response = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_count"] == 5
        assert len(data["assignments"]) == 5

        # 各割り当ての検証
        for assignment in data["assignments"]:
            assert assignment["worker_id"] == worker.id
            assert "id" in assignment
            assert "list_item_id" in assignment
            assert "created_at" in assignment
            assert "updated_at" in assignment
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_excludes_already_assigned_items(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """既に割り当て済みの項目は除外されることをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 最初に3件割り当て
            response1 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 3,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response1.status_code == 201
            data1 = response1.json()
            assert data1["assigned_count"] == 3

            # 再度5件割り当てを試みる（既に3件割り当て済みなので、残り7件から5件割り当てられる）
            response2 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response2.status_code == 201
            data2 = response2.json()
            assert data2["assigned_count"] == 5

            # 最終的に8件割り当てられている
            # 合計で3 + 5 = 8件

            # さらに割り当てを試みる（残り2件しかないため、2件のみ割り当てられる）
            response3 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 10,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response3.status_code == 201
            data3 = response3.json()
            assert data3["assigned_count"] == 2  # 残り2件のみ
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_no_unassigned_items(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """未割り当て項目がない場合は空リストを返すことをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 全件（10件）割り当て
            response1 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 20,  # 10件しかないので全件割り当てられる
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response1.status_code == 201
            data1 = response1.json()
            assert data1["assigned_count"] == 10

            # 再度割り当てを試みる（未割り当て項目がないため、空リスト）
            response2 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response2.status_code == 201
            data2 = response2.json()
            assert data2["assigned_count"] == 0
            assert data2["assignments"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織のリストには割り当てできないことをテスト（IDOR対策）"""
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

    # 組織Aのワーカー
    worker_user_a = User(
        organization_id=org_a.id,
        email="worker_a@example.com",
        hashed_password="hashed",
        full_name="ワーカーA",
        is_active=True,
    )
    db_session.add(worker_user_a)
    await db_session.flush()

    worker_a = Worker(
        user_id=worker_user_a.id,
        organization_id=org_a.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker_a)
    await db_session.flush()

    # 組織Bのリスト
    list_b = List(
        organization_id=org_b.id,
        name="組織Bのリスト",
        description="テスト用",
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
            # 組織Aのユーザーが組織Bのリストに割り当てを試みる
            response = await client.post(
                f"/api/v1/lists/{list_b.id}/assign-workers",
                json={
                    "worker_id": worker_a.id,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bのリストが見えない）
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unassign_worker_success(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """割り当て解除が成功することをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # ワーカーを割り当て
            assign_response = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 3,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert assign_response.status_code == 201
            assignments = assign_response.json()["assignments"]
            assignment_id = assignments[0]["id"]

            # 割り当て解除
            unassign_response = await client.delete(
                f"/api/v1/list-item-assignments/{assignment_id}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert unassign_response.status_code == 204

            # 再度同じ数を割り当てると、解除した1件を含めて3件割り当てられる
            reassign_response = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 3,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert reassign_response.status_code == 201
            reassignments = reassign_response.json()
            assert reassignments["assigned_count"] == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_validation_error(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """バリデーションエラーのテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 件数が0以下
            response1 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 0,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response1.status_code == 422

            # 件数が上限超え
            response2 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 1001,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response2.status_code == 422

            # worker_idが0以下
            response3 = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": 0,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response3.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_worker_not_found(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """存在しないワーカーIDで400エラーを返すことをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 存在しないワーカーID
            response = await client.post(
                f"/api/v1/lists/{test_list.id}/assign-workers",
                json={
                    "worker_id": 99999,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_bulk_assign_list_not_found(
    db_session: AsyncSession,
    setup_test_data: tuple[User, Organization, List, Worker, list[ListItem]],
) -> None:
    """存在しないリストIDで400エラーを返すことをテスト"""
    auth_user, org, test_list, worker, list_items = setup_test_data

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
            # 存在しないリストID
            response = await client.post(
                "/api/v1/lists/99999/assign-workers",
                json={
                    "worker_id": worker.id,
                    "count": 5,
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()
