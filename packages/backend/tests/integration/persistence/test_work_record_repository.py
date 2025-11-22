"""
作業記録リポジトリの結合テスト

実際のデータベースを使用してWorkRecordRepositoryの動作を検証します。
"""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import WorkRecordNotFoundError
from src.infrastructure.persistence.models import Organization, User
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.list_item import ListItem
from src.infrastructure.persistence.models.list_item_assignment import ListItemAssignment
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.worker import Worker, WorkerStatus
from src.infrastructure.persistence.models.work_record import WorkRecordStatus
from src.infrastructure.persistence.repositories.cannot_send_reason_repository import CannotSendReasonRepository
from src.infrastructure.persistence.repositories.work_record_repository import WorkRecordRepository


@pytest.fixture
async def sales_company_organization(db_session: AsyncSession) -> Organization:
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
async def test_worker(
    db_session: AsyncSession, sales_company_organization: Organization
) -> Worker:
    """テスト用ワーカーを作成"""
    user = User(
        organization_id=sales_company_organization.id,
        email="worker@example.com",
        hashed_password="hashed_password_123",
        full_name="作業者太郎",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    worker = Worker(
        user_id=user.id,
        organization_id=sales_company_organization.id,
        status=WorkerStatus.ACTIVE,
    )
    db_session.add(worker)
    await db_session.flush()
    return worker


@pytest.fixture
async def test_list(
    db_session: AsyncSession, sales_company_organization: Organization
) -> List:
    """テスト用リストを作成"""
    list_obj = List(
        organization_id=sales_company_organization.id,
        name="テストリスト",
        status="pending",
    )
    db_session.add(list_obj)
    await db_session.flush()
    return list_obj


@pytest.fixture
async def test_list_item(db_session: AsyncSession, test_list: List) -> ListItem:
    """テスト用リストアイテムを作成"""
    list_item = ListItem(
        list_id=test_list.id,
        company_name="株式会社テスト",
        url="https://example.com",
    )
    db_session.add(list_item)
    await db_session.flush()
    return list_item


@pytest.fixture
async def test_assignment(
    db_session: AsyncSession, test_list_item: ListItem, test_worker: Worker
) -> ListItemAssignment:
    """テスト用割り当てを作成"""
    assignment = ListItemAssignment(
        list_item_id=test_list_item.id,
        worker_id=test_worker.id,
    )
    db_session.add(assignment)
    await db_session.flush()
    return assignment


@pytest.fixture
async def test_cannot_send_reason(db_session: AsyncSession) -> int:
    """テスト用送信不可理由を作成"""
    repo = CannotSendReasonRepository(db_session)
    reason = await repo.create(
        reason_code="FORM_NOT_FOUND",
        reason_name="フォームが見つからない",
    )
    return reason.id


class TestWorkRecordRepositoryCreate:
    """作業記録作成のテスト"""

    async def test_create_work_record_sent_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：送信済み作業記録を作成できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        started = datetime.now(timezone.utc)
        completed = started + timedelta(minutes=30)

        # Act
        record = await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=started,
            completed_at=completed,
            form_submission_result={"status_code": 200, "message": "送信成功"},
            notes="問題なく送信完了",
        )

        # Assert
        assert record.id > 0
        assert record.assignment_id == test_assignment.id
        assert record.worker_id == test_worker.id
        assert record.status == WorkRecordStatus.SENT
        assert record.started_at == started
        assert record.completed_at == completed
        assert record.form_submission_result == {"status_code": 200, "message": "送信成功"}
        assert record.cannot_send_reason_id is None
        assert record.notes == "問題なく送信完了"

    async def test_create_work_record_cannot_send_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
        test_cannot_send_reason: int,
    ) -> None:
        """正常系：送信不可作業記録を作成できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        started = datetime.now(timezone.utc)
        completed = started + timedelta(minutes=15)

        # Act
        record = await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=started,
            completed_at=completed,
            cannot_send_reason_id=test_cannot_send_reason,
            notes="フォームが見つからず",
        )

        # Assert
        assert record.id > 0
        assert record.status == WorkRecordStatus.CANNOT_SEND
        assert record.cannot_send_reason_id == test_cannot_send_reason
        assert record.form_submission_result is None


class TestWorkRecordRepositoryFind:
    """作業記録検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：IDで作業記録を検索できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        created = await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        record = await repo.find_by_id(created.id)

        # Assert
        assert record is not None
        assert record.id == created.id
        assert record.status == WorkRecordStatus.SENT

    async def test_find_by_id_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = WorkRecordRepository(db_session)

        # Act
        record = await repo.find_by_id(999999)

        # Assert
        assert record is None

    async def test_find_by_assignment_id_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：割り当てIDで作業記録を検索できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        records = await repo.find_by_assignment_id(test_assignment.id)

        # Assert
        assert len(records) == 2
        assert all(r.assignment_id == test_assignment.id for r in records)

    async def test_find_by_worker_id_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：ワーカーIDで作業記録を検索できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        records = await repo.find_by_worker_id(test_worker.id)

        # Assert
        assert len(records) >= 1
        assert all(r.worker_id == test_worker.id for r in records)

    async def test_find_by_worker_id_with_status_filter(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：ステータスでフィルタリングできる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.CANNOT_SEND,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        sent_records = await repo.find_by_worker_id(test_worker.id, status=WorkRecordStatus.SENT)
        cannot_send_records = await repo.find_by_worker_id(test_worker.id, status=WorkRecordStatus.CANNOT_SEND)

        # Assert
        assert len(sent_records) >= 1
        assert all(r.status == WorkRecordStatus.SENT for r in sent_records)
        assert len(cannot_send_records) >= 1
        assert all(r.status == WorkRecordStatus.CANNOT_SEND for r in cannot_send_records)

    async def test_count_by_worker_id_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：ワーカーIDで作業記録の件数をカウントできる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        initial_count = await repo.count_by_worker_id(test_worker.id)

        # 2件追加
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        count = await repo.count_by_worker_id(test_worker.id)

        # Assert
        assert count == initial_count + 2


class TestWorkRecordRepositoryUpdate:
    """作業記録更新のテスト"""

    async def test_update_work_record_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
        test_cannot_send_reason: int,
    ) -> None:
        """正常系：作業記録を更新できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        record = await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        record.status = WorkRecordStatus.CANNOT_SEND
        record.cannot_send_reason_id = test_cannot_send_reason
        record.notes = "実際は送信失敗"
        updated = await repo.update(record)

        # Assert
        assert updated.id == record.id
        assert updated.status == WorkRecordStatus.CANNOT_SEND
        assert updated.cannot_send_reason_id == test_cannot_send_reason
        assert updated.notes == "実際は送信失敗"

    async def test_update_work_record_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """異常系：存在しない作業記録の更新でエラー"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        from src.domain.entities.work_record_entity import WorkRecordEntity

        fake_entity = WorkRecordEntity(
            id=999999,
            assignment_id=1,
            worker_id=1,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act & Assert
        with pytest.raises(WorkRecordNotFoundError):
            await repo.update(fake_entity)


class TestWorkRecordRepositorySoftDelete:
    """作業記録論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        test_assignment: ListItemAssignment,
        test_worker: Worker,
    ) -> None:
        """正常系：作業記録を論理削除できる"""
        # Arrange
        repo = WorkRecordRepository(db_session)
        record = await repo.create(
            assignment_id=test_assignment.id,
            worker_id=test_worker.id,
            status=WorkRecordStatus.SENT,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        # Act
        await repo.soft_delete(record.id)

        # Assert
        deleted = await repo.find_by_id(record.id)
        assert deleted is None

    async def test_soft_delete_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """異常系：存在しない作業記録の論理削除でエラー"""
        # Arrange
        repo = WorkRecordRepository(db_session)

        # Act & Assert
        with pytest.raises(WorkRecordNotFoundError):
            await repo.soft_delete(999999)
