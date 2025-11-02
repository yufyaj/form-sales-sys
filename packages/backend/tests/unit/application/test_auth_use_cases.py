"""
認証UseCaseの単体テスト

モックを使用してUseCaseのロジックを検証します。
リポジトリはモックで代替し、ビジネスロジックのみをテストします。
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.app.core.security import hash_password, verify_password
from src.application.use_cases.auth_use_cases import LoginUseCase, RegisterUserUseCase
from src.domain.entities.user_entity import UserEntity
from src.domain.exceptions import DuplicateEmailError, InactiveUserError, InvalidCredentialsError


class TestRegisterUserUseCase:
    """ユーザー登録UseCaseのテスト"""

    async def test_execute_success(self) -> None:
        """正常系：ユーザーを登録できる"""
        # Arrange
        mock_repo = AsyncMock()
        mock_user = Mock(spec=UserEntity)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_repo.create = AsyncMock(return_value=mock_user)

        use_case = RegisterUserUseCase(mock_repo)

        # Act
        user = await use_case.execute(
            organization_id=1,
            email="test@example.com",
            password="password123",
            full_name="テストユーザー",
        )

        # Assert
        assert user.id == 1
        assert user.email == "test@example.com"
        mock_repo.create.assert_called_once()

        # パスワードがハッシュ化されているか確認
        call_args = mock_repo.create.call_args
        assert "hashed_password" in call_args.kwargs
        hashed = call_args.kwargs["hashed_password"]
        assert verify_password("password123", hashed)

    async def test_execute_duplicate_email(self) -> None:
        """異常系：重複メールアドレスでエラー"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(side_effect=DuplicateEmailError("test@example.com"))

        use_case = RegisterUserUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            await use_case.execute(
                organization_id=1,
                email="test@example.com",
                password="password123",
                full_name="テストユーザー",
            )


class TestLoginUseCase:
    """ログインUseCaseのテスト"""

    async def test_execute_success(self) -> None:
        """正常系：ログインできる"""
        # Arrange
        mock_repo = AsyncMock()
        hashed_pw = hash_password("password123")

        mock_user = Mock(spec=UserEntity)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.organization_id = 1
        mock_user.hashed_password = hashed_pw
        mock_user.can_login = Mock(return_value=True)

        mock_repo.find_by_email = AsyncMock(return_value=mock_user)

        use_case = LoginUseCase(mock_repo)

        # Act
        user, token = await use_case.execute("test@example.com", "password123")

        # Assert
        assert user.id == 1
        assert user.email == "test@example.com"
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_execute_user_not_found(self) -> None:
        """異常系：ユーザーが見つからない"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.find_by_email = AsyncMock(return_value=None)

        use_case = LoginUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute("notfound@example.com", "password123")

    async def test_execute_wrong_password(self) -> None:
        """異常系：パスワードが間違っている"""
        # Arrange
        mock_repo = AsyncMock()
        hashed_pw = hash_password("correct_password")

        mock_user = Mock(spec=UserEntity)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.hashed_password = hashed_pw

        mock_repo.find_by_email = AsyncMock(return_value=mock_user)

        use_case = LoginUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute("test@example.com", "wrong_password")

    async def test_execute_inactive_user(self) -> None:
        """異常系：無効化されたユーザー"""
        # Arrange
        mock_repo = AsyncMock()
        hashed_pw = hash_password("password123")

        mock_user = Mock(spec=UserEntity)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.hashed_password = hashed_pw
        mock_user.can_login = Mock(return_value=False)

        mock_repo.find_by_email = AsyncMock(return_value=mock_user)

        use_case = LoginUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(InactiveUserError):
            await use_case.execute("test@example.com", "password123")
