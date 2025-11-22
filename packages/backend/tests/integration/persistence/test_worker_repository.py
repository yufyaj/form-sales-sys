"""
ワーカーリポジトリの結合テスト

実際のデータベースを使用してWorkerRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import WorkerNotFoundError
from src.infrastructure.persistence.models import Organization, User
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus
from src.infrastructure.persistence.repositories.worker_repository import WorkerRepository


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
async def test_user(
    db_session: AsyncSession, sales_company_organization: Organization
) -> User:
    """テスト用ユーザーを作成"""
    user = User(
        organization_id=sales_company_organization.id,
        email="worker1@example.com",
        hashed_password="hashed_password_123",
        full_name="山田太郎",
        phone="090-1234-5678",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_user2(
    db_session: AsyncSession, sales_company_organization: Organization
) -> User:
    """テスト用ユーザー2を作成"""
    user = User(
        organization_id=sales_company_organization.id,
        email="worker2@example.com",
        hashed_password="hashed_password_456",
        full_name="佐藤花子",
        phone="090-9876-5432",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


class TestWorkerRepositoryCreate:
    """ワーカー作成のテスト"""

    async def test_create_worker_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：ワーカーを作成できる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # Act
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
            skill_level=SkillLevel.INTERMEDIATE,
            experience_months=12,
            specialties="Python, FastAPI",
            max_tasks_per_day=10,
            available_hours_per_week=40,
            notes="テストワーカー",
        )

        # Assert
        assert worker.id > 0
        assert worker.user_id == test_user.id
        assert worker.organization_id == sales_company_organization.id
        assert worker.status == WorkerStatus.ACTIVE
        assert worker.skill_level == SkillLevel.INTERMEDIATE
        assert worker.experience_months == 12
        assert worker.specialties == "Python, FastAPI"
        assert worker.max_tasks_per_day == 10
        assert worker.available_hours_per_week == 40
        assert worker.notes == "テストワーカー"
        assert worker.completed_tasks_count == 0

    async def test_create_worker_minimal(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：必須項目のみでワーカーを作成できる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # Act
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
        )

        # Assert
        assert worker.id > 0
        assert worker.user_id == test_user.id
        assert worker.organization_id == sales_company_organization.id
        assert worker.status == WorkerStatus.PENDING
        assert worker.skill_level is None
        assert worker.experience_months is None
        assert worker.specialties is None
        assert worker.notes is None


class TestWorkerRepositoryFind:
    """ワーカー検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：IDでワーカーを検索できる"""
        # Arrange
        repo = WorkerRepository(db_session)
        created = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
            skill_level=SkillLevel.ADVANCED,
        )

        # Act
        worker = await repo.find_by_id(created.id, sales_company_organization.id)

        # Assert
        assert worker is not None
        assert worker.id == created.id
        assert worker.status == WorkerStatus.ACTIVE
        assert worker.skill_level == SkillLevel.ADVANCED

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = WorkerRepository(db_session)

        # Act
        worker = await repo.find_by_id(999999, sales_company_organization.id)

        # Assert
        assert worker is None

    async def test_find_by_id_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：異なる組織IDでの検索はNoneを返す（IDOR対策）"""
        # Arrange
        repo = WorkerRepository(db_session)
        created = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act
        worker = await repo.find_by_id(created.id, another_org.id)

        # Assert
        assert worker is None

    async def test_find_by_user_id_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：ユーザーIDでワーカーを検索できる"""
        # Arrange
        repo = WorkerRepository(db_session)
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # Act
        worker = await repo.find_by_user_id(test_user.id, sales_company_organization.id)

        # Assert
        assert worker is not None
        assert worker.user_id == test_user.id
        assert worker.status == WorkerStatus.ACTIVE

    async def test_list_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：組織IDでワーカー一覧を取得できる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 2人のワーカーを作成
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
        )

        # Act
        worker_list = await repo.list_by_organization(sales_company_organization.id)

        # Assert
        assert len(worker_list) == 2
        assert all(w.organization_id == sales_company_organization.id for w in worker_list)

    async def test_list_by_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：ステータスでフィルタリングできる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 2人のワーカーを作成（異なるステータス）
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
        )

        # Act
        active_workers = await repo.list_by_organization(
            sales_company_organization.id, status=WorkerStatus.ACTIVE
        )
        pending_workers = await repo.list_by_organization(
            sales_company_organization.id, status=WorkerStatus.PENDING
        )

        # Assert
        assert len(active_workers) == 1
        assert active_workers[0].status == WorkerStatus.ACTIVE
        assert len(pending_workers) == 1
        assert pending_workers[0].status == WorkerStatus.PENDING

    async def test_list_by_organization_pagination(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
    ) -> None:
        """正常系：ページネーションが機能する"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 3人のワーカーを作成
        for i in range(3):
            user = User(
                organization_id=sales_company_organization.id,
                email=f"worker{i+10}@example.com",
                hashed_password="hashed_password",
                full_name=f"テスト{i+1}",
                is_active=True,
            )
            db_session.add(user)
            await db_session.flush()
            await repo.create(
                user_id=user.id,
                organization_id=sales_company_organization.id,
                status=WorkerStatus.ACTIVE,
            )

        # Act
        first_page = await repo.list_by_organization(
            sales_company_organization.id, skip=0, limit=2
        )
        second_page = await repo.list_by_organization(
            sales_company_organization.id, skip=2, limit=2
        )

        # Assert
        assert len(first_page) == 2
        assert len(second_page) == 1

    async def test_count_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：組織IDでワーカー総件数を取得できる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 2人のワーカーを作成
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
        )

        # Act
        count = await repo.count_by_organization(sales_company_organization.id)

        # Assert
        assert count == 2

    async def test_count_by_organization_with_status_filter(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：ステータスでフィルタリングしてカウントできる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 2人のワーカーを作成（異なるステータス）
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
        )

        # Act
        active_count = await repo.count_by_organization(
            sales_company_organization.id, status=WorkerStatus.ACTIVE
        )
        pending_count = await repo.count_by_organization(
            sales_company_organization.id, status=WorkerStatus.PENDING
        )

        # Assert
        assert active_count == 1
        assert pending_count == 1

    async def test_count_by_organization_excludes_deleted(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：削除済みワーカーを除外してカウントできる"""
        # Arrange
        repo = WorkerRepository(db_session)

        # 2人のワーカーを作成
        worker1 = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # 1人を削除
        await repo.soft_delete(worker1.id, sales_company_organization.id)

        # Act
        count = await repo.count_by_organization(sales_company_organization.id)
        count_with_deleted = await repo.count_by_organization(
            sales_company_organization.id, include_deleted=True
        )

        # Assert
        assert count == 1  # 削除済みを除外
        assert count_with_deleted == 2  # 削除済みを含む


class TestWorkerRepositoryUpdate:
    """ワーカー更新のテスト"""

    async def test_update_worker_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：ワーカーを更新できる"""
        # Arrange
        repo = WorkerRepository(db_session)
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
            skill_level=SkillLevel.BEGINNER,
        )

        # Act
        worker.status = WorkerStatus.ACTIVE
        worker.skill_level = SkillLevel.INTERMEDIATE
        worker.experience_months = 6
        worker.notes = "スキルアップ"
        updated = await repo.update(worker, sales_company_organization.id)

        # Assert
        assert updated.id == worker.id
        assert updated.status == WorkerStatus.ACTIVE
        assert updated.skill_level == SkillLevel.INTERMEDIATE
        assert updated.experience_months == 6
        assert updated.notes == "スキルアップ"

    async def test_update_worker_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """異常系：存在しないワーカーの更新でエラー"""
        # Arrange
        repo = WorkerRepository(db_session)
        from src.domain.entities.worker_entity import WorkerEntity

        fake_entity = WorkerEntity(
            id=999999,
            user_id=1,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # Act & Assert
        with pytest.raises(WorkerNotFoundError):
            await repo.update(fake_entity, sales_company_organization.id)

    async def test_update_worker_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """異常系：異なる組織IDでの更新でエラー（IDOR対策）"""
        # Arrange
        repo = WorkerRepository(db_session)
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.PENDING,
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act & Assert
        worker.status = WorkerStatus.ACTIVE
        with pytest.raises(WorkerNotFoundError):
            await repo.update(worker, another_org.id)


class TestWorkerRepositorySoftDelete:
    """ワーカー論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：ワーカーを論理削除できる"""
        # Arrange
        repo = WorkerRepository(db_session)
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # Act
        await repo.soft_delete(worker.id, sales_company_organization.id)

        # Assert
        deleted = await repo.find_by_id(worker.id, sales_company_organization.id)
        assert deleted is None

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """異常系：存在しないワーカーの論理削除でエラー"""
        # Arrange
        repo = WorkerRepository(db_session)

        # Act & Assert
        with pytest.raises(WorkerNotFoundError):
            await repo.soft_delete(999999, sales_company_organization.id)

    async def test_soft_delete_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """異常系：異なる組織IDでの論理削除でエラー（IDOR対策）"""
        # Arrange
        repo = WorkerRepository(db_session)
        worker = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            status=WorkerStatus.ACTIVE,
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act & Assert
        with pytest.raises(WorkerNotFoundError):
            await repo.soft_delete(worker.id, another_org.id)
