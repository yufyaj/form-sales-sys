"""
リスト項目割り当てリポジトリの結合テスト

実際のデータベースを使用してListItemAssignmentRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import (
    DuplicateAssignmentError,
    ListItemAssignmentNotFoundError,
    ListItemNotFoundError,
    WorkerNotFoundError,
)
from src.infrastructure.persistence.models import (
    List,
    ListItem,
    Organization,
    User,
    Worker,
)
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.worker import WorkerStatus
from src.infrastructure.persistence.repositories.list_item_assignment_repository import (
    ListItemAssignmentRepository,
)
from src.infrastructure.persistence.repositories.list_item_repository import (
    ListItemRepository,
)
from src.infrastructure.persistence.repositories.list_repository import ListRepository


@pytest.fixture
async def sales_support_organization(db_session: AsyncSession) -> Organization:
    """テスト用営業支援会社組織を作成"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def another_sales_support_organization(db_session: AsyncSession) -> Organization:
    """テスト用の別の営業支援会社組織を作成（テナント分離テスト用）"""
    org = Organization(
        name="別の営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="another@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def test_user(
    db_session: AsyncSession, sales_support_organization: Organization
) -> User:
    """テスト用ユーザーを作成"""
    user = User(
        organization_id=sales_support_organization.id,
        email="worker@example.com",
        hashed_password="hashed_password",
        full_name="テストワーカー",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_worker(
    db_session: AsyncSession, sales_support_organization: Organization, test_user: User
) -> Worker:
    """テスト用ワーカーを作成"""
    worker = Worker(
        user_id=test_user.id,
        organization_id=sales_support_organization.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker)
    await db_session.flush()
    return worker


@pytest.fixture
async def another_test_user(
    db_session: AsyncSession, sales_support_organization: Organization
) -> User:
    """テスト用の別のユーザーを作成"""
    user = User(
        organization_id=sales_support_organization.id,
        email="worker2@example.com",
        hashed_password="hashed_password",
        full_name="テストワーカー2",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def another_test_worker(
    db_session: AsyncSession,
    sales_support_organization: Organization,
    another_test_user: User,
) -> Worker:
    """テスト用の別のワーカーを作成"""
    worker = Worker(
        user_id=another_test_user.id,
        organization_id=sales_support_organization.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker)
    await db_session.flush()
    return worker


@pytest.fixture
async def test_list(
    db_session: AsyncSession, sales_support_organization: Organization
) -> List:
    """テスト用リストを作成"""
    repo = ListRepository(db_session)
    list_entity = await repo.create(
        organization_id=sales_support_organization.id,
        name="IT企業リスト",
        description="テスト用リスト",
    )
    # DBモデルを取得して返す
    from sqlalchemy import select

    stmt = select(List).where(List.id == list_entity.id)
    result = await db_session.execute(stmt)
    return result.scalar_one()


@pytest.fixture
async def test_list_item(
    db_session: AsyncSession,
    sales_support_organization: Organization,
    test_list: List,
) -> ListItem:
    """テスト用リスト項目を作成"""
    repo = ListItemRepository(db_session)
    item_entity = await repo.create(
        list_id=test_list.id,
        title="株式会社テスト",
        status="pending",
    )
    # DBモデルを取得して返す
    from sqlalchemy import select

    stmt = select(ListItem).where(ListItem.id == item_entity.id)
    result = await db_session.execute(stmt)
    return result.scalar_one()


@pytest.fixture
async def another_test_list_item(
    db_session: AsyncSession,
    sales_support_organization: Organization,
    test_list: List,
) -> ListItem:
    """テスト用の別のリスト項目を作成"""
    repo = ListItemRepository(db_session)
    item_entity = await repo.create(
        list_id=test_list.id,
        title="株式会社サンプル",
        status="pending",
    )
    # DBモデルを取得して返す
    from sqlalchemy import select

    stmt = select(ListItem).where(ListItem.id == item_entity.id)
    result = await db_session.execute(stmt)
    return result.scalar_one()


class TestListItemAssignmentRepositoryAssign:
    """ワーカー割り当てのテスト"""

    async def test_assign_worker_to_list_item_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：リスト項目にワーカーを割り当てできる"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act
        assignment = await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert assignment.id > 0
        assert assignment.list_item_id == test_list_item.id
        assert assignment.worker_id == test_worker.id
        assert assignment.created_at is not None
        assert assignment.updated_at is not None

    async def test_assign_worker_duplicate_assignment_error(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """異常系：同じワーカーを同じリスト項目に複数回割り当てできない（重複防止）"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act & Assert - 重複割り当てでエラー
        with pytest.raises(DuplicateAssignmentError):
            await repo.assign_worker_to_list_item(
                list_item_id=test_list_item.id,
                worker_id=test_worker.id,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_assign_worker_list_item_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_worker: Worker,
    ) -> None:
        """異常系：存在しないリスト項目への割り当てでエラー"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act & Assert
        with pytest.raises(ListItemNotFoundError):
            await repo.assign_worker_to_list_item(
                list_item_id=999999,
                worker_id=test_worker.id,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_assign_worker_worker_not_found(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
    ) -> None:
        """異常系：存在しないワーカーの割り当てでエラー"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act & Assert
        with pytest.raises(WorkerNotFoundError):
            await repo.assign_worker_to_list_item(
                list_item_id=test_list_item.id,
                worker_id=999999,
                requesting_organization_id=sales_support_organization.id,
            )

    async def test_assign_worker_different_tenant_list_item(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        another_sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """セキュリティ：異なるテナントのリスト項目への割り当てはエラー（IDOR対策）"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act & Assert - テナントBからテナントAのリスト項目に割り当てを試みる
        with pytest.raises(ListItemNotFoundError):
            await repo.assign_worker_to_list_item(
                list_item_id=test_list_item.id,
                worker_id=test_worker.id,
                requesting_organization_id=another_sales_support_organization.id,
            )


class TestListItemAssignmentRepositoryFind:
    """割り当て検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：IDで割り当てを検索できる"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        created = await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act
        assignment = await repo.find_by_id(
            created.id, sales_support_organization.id
        )

        # Assert
        assert assignment is not None
        assert assignment.id == created.id
        assert assignment.list_item_id == test_list_item.id
        assert assignment.worker_id == test_worker.id

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act
        assignment = await repo.find_by_id(999999, sales_support_organization.id)

        # Assert
        assert assignment is None

    async def test_list_by_list_item_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
        another_test_worker: Worker,
    ) -> None:
        """正常系：リスト項目に割り当てられたワーカーの一覧を取得できる"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )
        await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=another_test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act
        assignments = await repo.list_by_list_item_id(
            test_list_item.id, sales_support_organization.id
        )

        # Assert
        assert len(assignments) == 2
        worker_ids = {a.worker_id for a in assignments}
        assert test_worker.id in worker_ids
        assert another_test_worker.id in worker_ids

    async def test_list_by_worker_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        another_test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：ワーカーに割り当てられたリスト項目の一覧を取得できる"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )
        await repo.assign_worker_to_list_item(
            list_item_id=another_test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act
        assignments = await repo.list_by_worker_id(
            test_worker.id, sales_support_organization.id
        )

        # Assert
        assert len(assignments) == 2
        list_item_ids = {a.list_item_id for a in assignments}
        assert test_list_item.id in list_item_ids
        assert another_test_list_item.id in list_item_ids


class TestListItemAssignmentRepositoryUnassign:
    """ワーカー割り当て解除のテスト"""

    async def test_unassign_worker_from_list_item_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：リスト項目からワーカーの割り当てを解除できる"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        assignment = await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act
        await repo.unassign_worker_from_list_item(
            assignment.id, sales_support_organization.id
        )

        # Assert - 削除されたことを確認
        deleted = await repo.find_by_id(assignment.id, sales_support_organization.id)
        assert deleted is None

    async def test_unassign_worker_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しない割り当ての解除でエラー"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act & Assert
        with pytest.raises(ListItemAssignmentNotFoundError):
            await repo.unassign_worker_from_list_item(
                999999, sales_support_organization.id
            )


class TestListItemAssignmentRepositoryCheckDuplicate:
    """重複割り当てチェックのテスト"""

    async def test_check_duplicate_assignment_not_exists(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：割り当てが存在しない場合はFalse"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)

        # Act
        is_duplicate = await repo.check_duplicate_assignment(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert is_duplicate is False

    async def test_check_duplicate_assignment_exists(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list_item: ListItem,
        test_worker: Worker,
    ) -> None:
        """正常系：割り当てが存在する場合はTrue"""
        # Arrange
        repo = ListItemAssignmentRepository(db_session)
        await repo.assign_worker_to_list_item(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Act
        is_duplicate = await repo.check_duplicate_assignment(
            list_item_id=test_list_item.id,
            worker_id=test_worker.id,
            requesting_organization_id=sales_support_organization.id,
        )

        # Assert
        assert is_duplicate is True
