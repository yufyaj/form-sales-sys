"""
営業支援会社担当者リポジトリの結合テスト

実際のデータベースを使用してSalesCompanyStaffRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import SalesCompanyStaffNotFoundError
from src.infrastructure.persistence.models import Organization, User
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.sales_company_staff_repository import (
    SalesCompanyStaffRepository,
)


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
        email="staff1@example.com",
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
        email="staff2@example.com",
        hashed_password="hashed_password_456",
        full_name="佐藤花子",
        phone="090-9876-5432",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


class TestSalesCompanyStaffRepositoryCreate:
    """営業支援会社担当者作成のテスト"""

    async def test_create_staff_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：営業支援会社担当者を作成できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # Act
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
            position="課長",
            employee_number="EMP-001",
            notes="テスト担当者",
        )

        # Assert
        assert staff.id > 0
        assert staff.user_id == test_user.id
        assert staff.organization_id == sales_company_organization.id
        assert staff.department == "営業部"
        assert staff.position == "課長"
        assert staff.employee_number == "EMP-001"
        assert staff.notes == "テスト担当者"

    async def test_create_staff_minimal(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：必須項目のみで営業支援会社担当者を作成できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # Act
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
        )

        # Assert
        assert staff.id > 0
        assert staff.user_id == test_user.id
        assert staff.organization_id == sales_company_organization.id
        assert staff.department is None
        assert staff.position is None
        assert staff.employee_number is None
        assert staff.notes is None


class TestSalesCompanyStaffRepositoryFind:
    """営業支援会社担当者検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：IDで営業支援会社担当者を検索できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        created = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
            position="課長",
        )

        # Act
        staff = await repo.find_by_id(created.id, sales_company_organization.id)

        # Assert
        assert staff is not None
        assert staff.id == created.id
        assert staff.department == "営業部"
        assert staff.position == "課長"

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # Act
        staff = await repo.find_by_id(999999, sales_company_organization.id)

        # Assert
        assert staff is None

    async def test_find_by_id_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：異なる組織IDでの検索はNoneを返す（IDOR対策）"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        created = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act
        staff = await repo.find_by_id(created.id, another_org.id)

        # Assert
        assert staff is None

    async def test_find_by_user_id_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：ユーザーIDで営業支援会社担当者を検索できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="総務部",
        )

        # Act
        staff = await repo.find_by_user_id(test_user.id, sales_company_organization.id)

        # Assert
        assert staff is not None
        assert staff.user_id == test_user.id
        assert staff.department == "総務部"

    async def test_list_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：組織IDで担当者一覧を取得できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # 2人の担当者を作成
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            department="総務部",
        )

        # Act
        staff_list = await repo.list_by_organization(sales_company_organization.id)

        # Assert
        assert len(staff_list) == 2
        assert all(s.organization_id == sales_company_organization.id for s in staff_list)

    async def test_list_by_organization_pagination(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
    ) -> None:
        """正常系：ページネーションが機能する"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # 3人の担当者を作成
        for i in range(3):
            user = User(
                organization_id=sales_company_organization.id,
                email=f"staff{i+10}@example.com",
                hashed_password="hashed_password",
                full_name=f"テスト{i+1}",
                is_active=True,
            )
            db_session.add(user)
            await db_session.flush()
            await repo.create(
                user_id=user.id,
                organization_id=sales_company_organization.id,
                department=f"部署{i+1}",
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
        """正常系：組織IDで担当者総件数を取得できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # 2人の担当者を作成
        await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            department="総務部",
        )

        # Act
        count = await repo.count_by_organization(sales_company_organization.id)

        # Assert
        assert count == 2

    async def test_count_by_organization_excludes_deleted(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
        test_user2: User,
    ) -> None:
        """正常系：削除済み担当者を除外してカウントできる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # 2人の担当者を作成
        staff1 = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )
        await repo.create(
            user_id=test_user2.id,
            organization_id=sales_company_organization.id,
            department="総務部",
        )

        # 1人を削除
        await repo.soft_delete(staff1.id, sales_company_organization.id)

        # Act
        count = await repo.count_by_organization(sales_company_organization.id)
        count_with_deleted = await repo.count_by_organization(
            sales_company_organization.id, include_deleted=True
        )

        # Assert
        assert count == 1  # 削除済みを除外
        assert count_with_deleted == 2  # 削除済みを含む


class TestSalesCompanyStaffRepositoryUpdate:
    """営業支援会社担当者更新のテスト"""

    async def test_update_staff_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：営業支援会社担当者を更新できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
            position="主任",
        )

        # Act
        staff.department = "総務部"
        staff.position = "課長"
        staff.notes = "昇進"
        updated = await repo.update(staff, sales_company_organization.id)

        # Assert
        assert updated.id == staff.id
        assert updated.department == "総務部"
        assert updated.position == "課長"
        assert updated.notes == "昇進"

    async def test_update_staff_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """異常系：存在しない担当者の更新でエラー"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        from src.domain.entities.sales_company_staff_entity import (
            SalesCompanyStaffEntity,
        )

        fake_entity = SalesCompanyStaffEntity(
            id=999999,
            user_id=1,
            organization_id=sales_company_organization.id,
            department="存在しない",
        )

        # Act & Assert
        with pytest.raises(SalesCompanyStaffNotFoundError):
            await repo.update(fake_entity, sales_company_organization.id)

    async def test_update_staff_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """異常系：異なる組織IDでの更新でエラー（IDOR対策）"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act & Assert
        staff.department = "総務部"
        with pytest.raises(SalesCompanyStaffNotFoundError):
            await repo.update(staff, another_org.id)


class TestSalesCompanyStaffRepositorySoftDelete:
    """営業支援会社担当者論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """正常系：営業支援会社担当者を論理削除できる"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )

        # Act
        await repo.soft_delete(staff.id, sales_company_organization.id)

        # Assert
        deleted = await repo.find_by_id(staff.id, sales_company_organization.id)
        assert deleted is None

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_company_organization: Organization
    ) -> None:
        """異常系：存在しない担当者の論理削除でエラー"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)

        # Act & Assert
        with pytest.raises(SalesCompanyStaffNotFoundError):
            await repo.soft_delete(999999, sales_company_organization.id)

    async def test_soft_delete_wrong_organization(
        self,
        db_session: AsyncSession,
        sales_company_organization: Organization,
        test_user: User,
    ) -> None:
        """異常系：異なる組織IDでの論理削除でエラー（IDOR対策）"""
        # Arrange
        repo = SalesCompanyStaffRepository(db_session)
        staff = await repo.create(
            user_id=test_user.id,
            organization_id=sales_company_organization.id,
            department="営業部",
        )

        # 別の組織を作成
        another_org = Organization(
            name="別の営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(another_org)
        await db_session.flush()

        # Act & Assert
        with pytest.raises(SalesCompanyStaffNotFoundError):
            await repo.soft_delete(staff.id, another_org.id)
