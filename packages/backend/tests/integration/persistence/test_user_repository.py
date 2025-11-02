"""
ユーザーリポジトリの結合テスト

実際のデータベースを使用してUserRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import DuplicateEmailError, UserNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.user_repository import UserRepository


@pytest.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """テスト用組織を作成"""
    org = Organization(
        name="テスト組織",
        type=OrganizationType.CLIENT,
        email="test@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


class TestUserRepositoryCreate:
    """ユーザー作成のテスト"""

    async def test_create_user_success(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """正常系：ユーザーを作成できる"""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        user = await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="テストユーザー",
            phone="090-1234-5678",
        )

        # Assert
        assert user.id > 0
        assert user.email == "test@example.com"
        assert user.full_name == "テストユーザー"
        assert user.phone == "090-1234-5678"
        assert user.organization_id == test_organization.id
        assert user.is_active is True
        assert user.is_email_verified is False

    async def test_create_user_duplicate_email(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """異常系：重複メールアドレスでエラー"""
        # Arrange
        repo = UserRepository(db_session)
        await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="ユーザー1",
        )

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            await repo.create(
                organization_id=test_organization.id,
                email="test@example.com",
                hashed_password="$2b$12$anotherpassword",
                full_name="ユーザー2",
            )


class TestUserRepositoryFind:
    """ユーザー検索のテスト"""

    async def test_find_by_id_success(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """正常系：IDでユーザーを検索できる"""
        # Arrange
        repo = UserRepository(db_session)
        created_user = await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="テストユーザー",
        )

        # Act
        user = await repo.find_by_id(created_user.id)

        # Assert
        assert user is not None
        assert user.id == created_user.id
        assert user.email == "test@example.com"

    async def test_find_by_id_not_found(self, db_session: AsyncSession) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        user = await repo.find_by_id(999999)

        # Assert
        assert user is None

    async def test_find_by_email_success(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """正常系：メールアドレスでユーザーを検索できる"""
        # Arrange
        repo = UserRepository(db_session)
        await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="テストユーザー",
        )

        # Act
        user = await repo.find_by_email("test@example.com")

        # Assert
        assert user is not None
        assert user.email == "test@example.com"

    async def test_find_by_email_not_found(self, db_session: AsyncSession) -> None:
        """正常系：存在しないメールアドレスはNoneを返す"""
        # Arrange
        repo = UserRepository(db_session)

        # Act
        user = await repo.find_by_email("notfound@example.com")

        # Assert
        assert user is None


class TestUserRepositoryUpdate:
    """ユーザー更新のテスト"""

    async def test_update_password_success(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """正常系：パスワードを更新できる"""
        # Arrange
        repo = UserRepository(db_session)
        user = await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$oldpassword",
            full_name="テストユーザー",
        )

        # Act
        updated_user = await repo.update_password(user.id, "$2b$12$newpassword")

        # Assert
        assert updated_user.hashed_password == "$2b$12$newpassword"

    async def test_update_password_not_found(self, db_session: AsyncSession) -> None:
        """異常系：存在しないユーザーのパスワード更新でエラー"""
        # Arrange
        repo = UserRepository(db_session)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repo.update_password(999999, "$2b$12$newpassword")

    async def test_verify_email_success(
        self, db_session: AsyncSession, test_organization: Organization
    ) -> None:
        """正常系：メール認証を完了できる"""
        # Arrange
        repo = UserRepository(db_session)
        user = await repo.create(
            organization_id=test_organization.id,
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            full_name="テストユーザー",
        )
        assert user.is_email_verified is False

        # Act
        verified_user = await repo.verify_email(user.id)

        # Assert
        assert verified_user.is_email_verified is True

    async def test_verify_email_not_found(self, db_session: AsyncSession) -> None:
        """異常系：存在しないユーザーのメール認証でエラー"""
        # Arrange
        repo = UserRepository(db_session)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await repo.verify_email(999999)
