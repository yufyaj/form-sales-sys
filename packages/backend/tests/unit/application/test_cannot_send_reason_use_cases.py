"""
送信不可理由UseCaseの単体テスト

モックを使用してUseCaseのロジックを検証します。
リポジトリはモックで代替し、ビジネスロジックのみをテストします。
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.schemas.cannot_send_reason import (
    CannotSendReasonCreateRequest,
    CannotSendReasonUpdateRequest,
)
from src.application.use_cases.cannot_send_reason_use_cases import (
    CannotSendReasonUseCases,
)
from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity
from src.domain.exceptions import (
    CannotSendReasonNotFoundError,
    DuplicateCannotSendReasonCodeError,
)


class TestCreateReason:
    """送信不可理由作成のテスト"""

    async def test_create_reason_success(self) -> None:
        """正常系：送信不可理由を作成できる"""
        # Arrange
        mock_repo = AsyncMock()
        mock_reason = Mock(spec=CannotSendReasonEntity)
        mock_reason.id = 1
        mock_reason.reason_code = "FORM_NOT_FOUND"
        mock_reason.reason_name = "フォームが見つからない"
        mock_reason.is_active = True

        mock_repo.find_by_reason_code = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=mock_reason)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        request = CannotSendReasonCreateRequest(
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            description="Webページにフォームが存在しない場合",
            is_active=True,
        )

        # Act
        reason = await use_cases.create_reason(request=request)

        # Assert
        assert reason.id == 1
        assert reason.reason_code == "FORM_NOT_FOUND"
        assert reason.reason_name == "フォームが見つからない"
        mock_repo.find_by_reason_code.assert_called_once_with(reason_code="FORM_NOT_FOUND")
        mock_repo.create.assert_called_once()

    async def test_create_reason_duplicate_code(self) -> None:
        """異常系：重複する理由コードでエラー"""
        # Arrange
        mock_repo = AsyncMock()
        existing_reason = Mock(spec=CannotSendReasonEntity)
        existing_reason.id = 1
        existing_reason.reason_code = "FORM_NOT_FOUND"

        mock_repo.find_by_reason_code = AsyncMock(return_value=existing_reason)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        request = CannotSendReasonCreateRequest(
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
        )

        # Act & Assert
        with pytest.raises(DuplicateCannotSendReasonCodeError):
            await use_cases.create_reason(request=request)


class TestGetReason:
    """送信不可理由取得のテスト"""

    async def test_get_reason_success(self) -> None:
        """正常系：送信不可理由を取得できる"""
        # Arrange
        mock_repo = AsyncMock()
        mock_reason = Mock(spec=CannotSendReasonEntity)
        mock_reason.id = 1
        mock_reason.reason_code = "FORM_NOT_FOUND"

        mock_repo.find_by_id = AsyncMock(return_value=mock_reason)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        # Act
        reason = await use_cases.get_reason(reason_id=1)

        # Assert
        assert reason.id == 1
        assert reason.reason_code == "FORM_NOT_FOUND"
        mock_repo.find_by_id.assert_called_once_with(reason_id=1)

    async def test_get_reason_not_found(self) -> None:
        """異常系：送信不可理由が見つからない"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        # Act & Assert
        with pytest.raises(CannotSendReasonNotFoundError):
            await use_cases.get_reason(reason_id=999)


class TestListReasons:
    """送信不可理由一覧取得のテスト"""

    async def test_list_reasons_success(self) -> None:
        """正常系：送信不可理由の一覧を取得できる"""
        # Arrange
        mock_repo = AsyncMock()
        mock_reasons = [
            Mock(spec=CannotSendReasonEntity, id=1, reason_code="FORM_NOT_FOUND"),
            Mock(spec=CannotSendReasonEntity, id=2, reason_code="CAPTCHA_REQUIRED"),
        ]

        mock_repo.list_all = AsyncMock(return_value=mock_reasons)
        mock_repo.count_all = AsyncMock(return_value=2)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        # Act
        reasons, total = await use_cases.list_reasons(
            is_active_only=True, skip=0, limit=100
        )

        # Assert
        assert len(reasons) == 2
        assert total == 2
        assert reasons[0].id == 1
        assert reasons[1].id == 2
        mock_repo.list_all.assert_called_once()
        mock_repo.count_all.assert_called_once()


class TestUpdateReason:
    """送信不可理由更新のテスト"""

    async def test_update_reason_success(self) -> None:
        """正常系：送信不可理由を更新できる"""
        # Arrange
        mock_repo = AsyncMock()
        existing_reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=True,
        )
        updated_reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない（更新）",
            is_active=False,
        )

        mock_repo.find_by_id = AsyncMock(return_value=existing_reason)
        mock_repo.update = AsyncMock(return_value=updated_reason)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        request = CannotSendReasonUpdateRequest(
            reason_name="フォームが見つからない（更新）",
            is_active=False,
        )

        # Act
        reason = await use_cases.update_reason(reason_id=1, request=request)

        # Assert
        assert reason.id == 1
        assert reason.reason_name == "フォームが見つからない（更新）"
        assert reason.is_active is False
        mock_repo.find_by_id.assert_called_once_with(reason_id=1)
        mock_repo.update.assert_called_once()

    async def test_update_reason_not_found(self) -> None:
        """異常系：更新対象が見つからない"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        request = CannotSendReasonUpdateRequest(reason_name="更新")

        # Act & Assert
        with pytest.raises(CannotSendReasonNotFoundError):
            await use_cases.update_reason(reason_id=999, request=request)

    async def test_update_reason_duplicate_code(self) -> None:
        """異常系：理由コード更新時に重複エラー"""
        # Arrange
        mock_repo = AsyncMock()
        existing_reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=True,
        )
        conflicting_reason = CannotSendReasonEntity(
            id=2,
            reason_code="CAPTCHA_REQUIRED",
            reason_name="CAPTCHA認証が必要",
            is_active=True,
        )

        mock_repo.find_by_id = AsyncMock(return_value=existing_reason)
        mock_repo.find_by_reason_code = AsyncMock(return_value=conflicting_reason)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        request = CannotSendReasonUpdateRequest(reason_code="CAPTCHA_REQUIRED")

        # Act & Assert
        with pytest.raises(DuplicateCannotSendReasonCodeError):
            await use_cases.update_reason(reason_id=1, request=request)


class TestDeleteReason:
    """送信不可理由削除のテスト"""

    async def test_delete_reason_success(self) -> None:
        """正常系：送信不可理由を削除できる"""
        # Arrange
        mock_repo = AsyncMock()
        existing_reason = Mock(spec=CannotSendReasonEntity)
        existing_reason.id = 1
        existing_reason.reason_code = "FORM_NOT_FOUND"

        mock_repo.find_by_id = AsyncMock(return_value=existing_reason)
        mock_repo.soft_delete = AsyncMock()

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        # Act
        await use_cases.delete_reason(reason_id=1)

        # Assert
        mock_repo.find_by_id.assert_called_once_with(reason_id=1)
        mock_repo.soft_delete.assert_called_once_with(reason_id=1)

    async def test_delete_reason_not_found(self) -> None:
        """異常系：削除対象が見つからない"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        use_cases = CannotSendReasonUseCases(cannot_send_reason_repository=mock_repo)

        # Act & Assert
        with pytest.raises(CannotSendReasonNotFoundError):
            await use_cases.delete_reason(reason_id=999)
