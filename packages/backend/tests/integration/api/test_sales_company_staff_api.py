"""
営業支援会社担当者API統合テスト

実際のデータベースを使用してAPIエンドポイントをテストします
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.main import app
from src.infrastructure.persistence.models.organization import (
    Organization,
    OrganizationType,
)
from src.infrastructure.persistence.models.user import User


@pytest.mark.asyncio
async def test_create_staff_success(db_session: AsyncSession) -> None:
    """営業支援会社担当者作成が成功することをテスト"""
    # テスト用営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    # テスト用ユーザーを作成
    user = User(
        organization_id=org.id,
        email="staff@example.com",
        hashed_password="hashed_password",
        full_name="山田太郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # FastAPIアプリのDB依存性をオーバーライド
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        # HTTPクライアントでAPIをテスト
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
        # オーバーライドをクリア
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_staff_success(db_session: AsyncSession) -> None:
    """営業支援会社担当者取得が成功することをテスト"""
    # テスト用営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    # テスト用ユーザーを作成
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

    app.dependency_overrides[get_db] = override_get_db

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
            )
            created_staff = create_response.json()

            # 担当者を取得
            response = await client.get(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
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
async def test_list_staff_success(db_session: AsyncSession) -> None:
    """営業支援会社担当者一覧取得が成功することをテスト"""
    # テスト用営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

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

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/sales-company-staff",
                json={
                    "user_id": user.id,
                    "department": f"部署{i+1}",
                },
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 担当者一覧を取得
            response = await client.get(
                "/api/v1/sales-company-staff",
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["staff"]) == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_staff_success(db_session: AsyncSession) -> None:
    """営業支援会社担当者更新が成功することをテスト"""
    # テスト用営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    # テスト用ユーザーを作成
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

    app.dependency_overrides[get_db] = override_get_db

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
            )
            created_staff = create_response.json()

            # 担当者を更新
            response = await client.patch(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
                json={"position": "課長", "notes": "昇進"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["position"] == "課長"
        assert data["notes"] == "昇進"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_staff_success(db_session: AsyncSession) -> None:
    """営業支援会社担当者削除が成功することをテスト"""
    # テスト用営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    # テスト用ユーザーを作成
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

    app.dependency_overrides[get_db] = override_get_db

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
            )
            created_staff = create_response.json()

            # 担当者を削除
            response = await client.delete(
                f"/api/v1/sales-company-staff/{created_staff['id']}",
            )

        # レスポンス検証
        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()
