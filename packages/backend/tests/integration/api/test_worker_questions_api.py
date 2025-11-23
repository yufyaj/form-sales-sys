"""
ワーカー質問API統合テスト（認証対応版）

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
from src.infrastructure.persistence.models.worker import Worker, WorkerStatus


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
async def worker_and_org(db_session: AsyncSession, auth_user_and_org: tuple[User, Organization]) -> tuple[Worker, Organization]:
    """ワーカーと組織のフィクスチャ"""
    auth_user, org = auth_user_and_org

    # ワーカー用ユーザーを作成
    worker_user = User(
        organization_id=org.id,
        email="worker@example.com",
        hashed_password="hashed_password",
        full_name="ワーカー太郎",
        is_active=True,
    )
    db_session.add(worker_user)
    await db_session.flush()

    # ワーカーを作成
    worker = Worker(
        user_id=worker_user.id,
        organization_id=org.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker)
    await db_session.flush()

    return worker, org


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


@pytest.mark.asyncio
async def test_create_question_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """ワーカー質問作成が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
                "/api/v1/worker-questions",
                json={
                    "title": "フォーム入力の手順について",
                    "content": "〇〇フォームの入力手順がわからないため、教えていただけますでしょうか。",
                    "priority": "medium",
                    "tags": '["フォーム入力", "操作方法"]',
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "フォーム入力の手順について"
        assert data["content"] == "〇〇フォームの入力手順がわからないため、教えていただけますでしょうか。"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"
        assert data["organization_id"] == org.id
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_question_unauthorized(db_session: AsyncSession) -> None:
    """認証なしの場合は401エラーを返すことをテスト"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "テスト質問",
                    "content": "テスト内容",
                },
                # 認証ヘッダーなし
            )

        # 401 Unauthorized を期待
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_question_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """ワーカー質問取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "テスト質問",
                    "content": "これはテスト質問です",
                    "priority": "high",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 質問を取得
            response = await client.get(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_question["id"]
        assert data["title"] == "テスト質問"
        assert data["priority"] == "high"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_question_cross_tenant_forbidden(
    db_session: AsyncSession,
) -> None:
    """別組織の質問取得は404エラーを返すことをテスト（IDOR対策）"""
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

    worker_b = Worker(
        user_id=user_b.id,
        organization_id=org_b.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker_b)
    await db_session.flush()

    # 組織Bの認証ユーザー
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

    # 組織Bで質問を作成
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            "/api/v1/worker-questions",
            json={
                "title": "組織Bの質問",
                "content": "これは組織Bの質問です",
            },
            headers={"Authorization": "Bearer mock_token"},
        )
        created_question = create_response.json()

    # 組織Aのユーザーで組織Bの質問を取得しようとする
    async def override_get_current_active_user_a():
        return create_user_entity(auth_user_a)

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user_a

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待（組織Aからは組織Bの質問が見えない）
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_questions_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """質問一覧取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # 複数の質問を作成
    for i in range(3):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": f"質問{i+1}",
                    "content": f"これは質問{i+1}です",
                    "priority": "medium" if i % 2 == 0 else "high",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 質問一覧を取得
            response = await client.get(
                "/api/v1/worker-questions",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["questions"]) == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_questions_with_status_filter(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """ステータスフィルタ付き質問一覧取得をテスト"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # 質問を作成（pendingステータス）
    for i in range(2):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": f"未回答質問{i+1}",
                    "content": f"内容{i+1}",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # pendingステータスの質問のみ取得
            response = await client.get(
                "/api/v1/worker-questions?status=pending",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for question in data["questions"]:
            assert question["status"] == "pending"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_add_answer_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """質問への回答追加が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "回答テスト質問",
                    "content": "回答をお願いします",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 回答を追加
            response = await client.post(
                f"/api/v1/worker-questions/{created_question['id']}/answer",
                json={
                    "answer": "これが回答です。手順は以下の通りです。\n1. ...\n2. ...",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "これが回答です。手順は以下の通りです。\n1. ...\n2. ..."
        assert data["status"] == "answered"
        assert data["answered_by_user_id"] == auth_user.id
        assert data["answered_at"] is not None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_question_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """質問更新が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "元のタイトル",
                    "content": "元の内容",
                    "priority": "low",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 質問を更新
            response = await client.patch(
                f"/api/v1/worker-questions/{created_question['id']}",
                json={
                    "title": "更新後のタイトル",
                    "content": "更新後の内容",
                    "priority": "urgent",
                    "status": "in_review",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新後のタイトル"
        assert data["content"] == "更新後の内容"
        assert data["priority"] == "urgent"
        assert data["status"] == "in_review"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_question_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """質問削除が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "削除テスト",
                    "content": "削除される質問",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 質問を削除
            response = await client.delete(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 204

        # 削除後に取得できないことを確認
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            get_response = await client.get(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert get_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_unread_count_success_with_auth(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """未読質問数取得が成功することをテスト（認証付き）"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

    async def override_get_db():
        yield db_session

    async def override_get_current_active_user():
        return create_user_entity(auth_user)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # pending状態の質問を3件作成
    for i in range(3):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": f"未読質問{i+1}",
                    "content": f"内容{i+1}",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 未読質問数を取得
            response = await client.get(
                "/api/v1/worker-questions/stats/unread-count",
                headers={"Authorization": "Bearer mock_token"},
            )

        # レスポンス検証
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 3
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_question_validation_error(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """バリデーションエラーのテスト"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # タイトルなしでエラー
            response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "content": "内容のみ",
                    # titleなし
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 422 Unprocessable Entity を期待
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_add_answer_to_already_answered_question(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """既に回答済みの質問に再度回答しようとすると400エラーを返すことをテスト"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "回答重複テスト",
                    "content": "一度だけ回答してください",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 1回目の回答（成功）
            first_answer_response = await client.post(
                f"/api/v1/worker-questions/{created_question['id']}/answer",
                json={
                    "answer": "最初の回答",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            assert first_answer_response.status_code == 200

            # 2回目の回答（失敗）
            second_answer_response = await client.post(
                f"/api/v1/worker-questions/{created_question['id']}/answer",
                json={
                    "answer": "2回目の回答",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 400 Bad Request を期待（既に回答済み）
        assert second_answer_response.status_code == 400
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_soft_deleted_question_returns_404(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """論理削除された質問を取得しようとすると404を返すことをテスト"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 質問を作成
            create_response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": "削除テスト",
                    "content": "この質問は削除されます",
                },
                headers={"Authorization": "Bearer mock_token"},
            )
            created_question = create_response.json()

            # 質問を削除
            delete_response = await client.delete(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )
            assert delete_response.status_code == 204

            # 削除後に取得しようとする
            get_response = await client.get(
                f"/api/v1/worker-questions/{created_question['id']}",
                headers={"Authorization": "Bearer mock_token"},
            )

        # 404 Not Found を期待
        assert get_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_question_with_long_title_validation_error(
    db_session: AsyncSession,
    auth_user_and_org: tuple[User, Organization],
    worker_and_org: tuple[Worker, Organization]
) -> None:
    """タイトルが500文字を超える場合に422エラーを返すことをテスト"""
    auth_user, org = auth_user_and_org
    worker, _ = worker_and_org

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
            # 501文字のタイトルを作成
            long_title = "あ" * 501

            response = await client.post(
                "/api/v1/worker-questions",
                json={
                    "title": long_title,
                    "content": "タイトルが長すぎます",
                },
                headers={"Authorization": "Bearer mock_token"},
            )

        # 422 Unprocessable Entity を期待
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
