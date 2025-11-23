"""
送信不可理由エンティティのユニットテスト

ビジネスロジックとバリデーションをテストします。
"""
from datetime import datetime

import pytest

from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity


class TestCannotSendReasonEntity:
    """CannotSendReasonEntityのテストクラス"""

    def test_create_reason_entity_with_minimal_fields(self) -> None:
        """最小限のフィールドで送信不可理由エンティティを作成"""
        # Arrange & Act
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
        )

        # Assert
        assert reason.id == 1
        assert reason.reason_code == "FORM_NOT_FOUND"
        assert reason.reason_name == "フォームが見つからない"
        assert reason.description is None
        assert reason.is_active is True
        assert reason.created_at is None
        assert reason.updated_at is None
        assert reason.deleted_at is None

    def test_create_reason_entity_with_all_fields(self) -> None:
        """全フィールドを指定して送信不可理由エンティティを作成"""
        # Arrange
        created = datetime(2025, 1, 1, 10, 0, 0)
        updated = datetime(2025, 1, 10, 15, 30, 0)

        # Act
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="CAPTCHA_REQUIRED",
            reason_name="CAPTCHA認証が必要",
            description="フォーム送信にCAPTCHA認証が必要な場合",
            is_active=True,
            created_at=created,
            updated_at=updated,
        )

        # Assert
        assert reason.id == 1
        assert reason.reason_code == "CAPTCHA_REQUIRED"
        assert reason.reason_name == "CAPTCHA認証が必要"
        assert reason.description == "フォーム送信にCAPTCHA認証が必要な場合"
        assert reason.is_active is True
        assert reason.created_at == created
        assert reason.updated_at == updated
        assert reason.deleted_at is None

    def test_is_deleted_returns_false_when_not_deleted(self) -> None:
        """論理削除されていない場合、is_deleted()はFalseを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            deleted_at=None,
        )

        # Act & Assert
        assert reason.is_deleted() is False

    def test_is_deleted_returns_true_when_deleted(self) -> None:
        """論理削除されている場合、is_deleted()はTrueを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert reason.is_deleted() is True

    def test_is_usable_returns_true_when_active_and_not_deleted(self) -> None:
        """有効かつ削除されていない場合、is_usable()はTrueを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=True,
            deleted_at=None,
        )

        # Act & Assert
        assert reason.is_usable() is True

    def test_is_usable_returns_false_when_inactive(self) -> None:
        """無効な場合、is_usable()はFalseを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=False,
            deleted_at=None,
        )

        # Act & Assert
        assert reason.is_usable() is False

    def test_is_usable_returns_false_when_deleted(self) -> None:
        """削除済みの場合、is_usable()はFalseを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=True,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert reason.is_usable() is False

    def test_is_usable_returns_false_when_inactive_and_deleted(self) -> None:
        """無効かつ削除済みの場合、is_usable()はFalseを返す"""
        # Arrange
        reason = CannotSendReasonEntity(
            id=1,
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            is_active=False,
            deleted_at=datetime.now(),
        )

        # Act & Assert
        assert reason.is_usable() is False

    def test_reason_with_various_reason_codes(self) -> None:
        """様々な理由コードで送信不可理由を作成できることを確認"""
        # Arrange & Act & Assert
        reason_codes = [
            ("FORM_NOT_FOUND", "フォームが見つからない"),
            ("CAPTCHA_REQUIRED", "CAPTCHA認証が必要"),
            ("INVALID_EMAIL", "メールアドレスが無効"),
            ("COMPANY_BLACKLISTED", "企業がブラックリストに登録済み"),
            ("NETWORK_ERROR", "ネットワークエラー"),
        ]

        for code, name in reason_codes:
            reason = CannotSendReasonEntity(
                id=1,
                reason_code=code,
                reason_name=name,
            )
            assert reason.reason_code == code
            assert reason.reason_name == name
