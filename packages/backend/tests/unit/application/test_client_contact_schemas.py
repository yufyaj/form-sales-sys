"""
顧客担当者スキーマの単体テスト

Pydantic v2のバリデーション機能をテストします。
"""
import pytest
from pydantic import ValidationError

from src.application.schemas.client_contact import (
    ClientContactCreateRequest,
    ClientContactResponse,
    ClientContactUpdateRequest,
)


class TestClientContactCreateRequest:
    """顧客担当者作成リクエストのテスト"""

    def test_create_request_valid(self) -> None:
        """正常系：有効なデータでスキーマを作成できる"""
        # Arrange & Act
        request = ClientContactCreateRequest(
            client_organization_id=1,
            full_name="田中一郎",
            department="営業部",
            position="部長",
            email="tanaka@example.com",
            phone="03-1234-5678",
            mobile="090-1234-5678",
            is_primary=True,
            notes="キーパーソン",
        )

        # Assert
        assert request.client_organization_id == 1
        assert request.full_name == "田中一郎"
        assert request.department == "営業部"
        assert request.position == "部長"
        assert request.email == "tanaka@example.com"
        assert request.phone == "03-1234-5678"
        assert request.mobile == "090-1234-5678"
        assert request.is_primary is True
        assert request.notes == "キーパーソン"

    def test_create_request_minimal(self) -> None:
        """正常系：必須項目のみでスキーマを作成できる"""
        # Arrange & Act
        request = ClientContactCreateRequest(
            client_organization_id=1,
            full_name="山田太郎",
        )

        # Assert
        assert request.client_organization_id == 1
        assert request.full_name == "山田太郎"
        assert request.department is None
        assert request.position is None
        assert request.email is None
        assert request.phone is None
        assert request.mobile is None
        assert request.is_primary is False

    def test_create_request_missing_full_name(self) -> None:
        """異常系：氏名が必須"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientContactCreateRequest(
                client_organization_id=1,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("full_name",) for error in errors)

    def test_create_request_invalid_email(self) -> None:
        """異常系：無効なメールアドレス形式はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientContactCreateRequest(
                client_organization_id=1,
                full_name="田中一郎",
                email="invalid-email",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_create_request_invalid_phone_too_short(self) -> None:
        """異常系：電話番号が10桁未満の場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientContactCreateRequest(
                client_organization_id=1,
                full_name="田中一郎",
                phone="03-1234",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("phone",) for error in errors)
        assert any(
            "10桁以上である必要があります" in str(error["ctx"]) for error in errors
        )

    def test_create_request_valid_phone_with_hyphens(self) -> None:
        """正常系：ハイフン付き電話番号は有効"""
        # Arrange & Act
        request = ClientContactCreateRequest(
            client_organization_id=1,
            full_name="田中一郎",
            phone="03-1234-5678",
        )

        # Assert
        assert request.phone == "03-1234-5678"

    def test_create_request_valid_phone_without_hyphens(self) -> None:
        """正常系：ハイフンなし電話番号は有効"""
        # Arrange & Act
        request = ClientContactCreateRequest(
            client_organization_id=1,
            full_name="田中一郎",
            phone="0312345678",
        )

        # Assert
        assert request.phone == "0312345678"

    def test_create_request_valid_mobile_with_hyphens(self) -> None:
        """正常系：ハイフン付き携帯番号は有効"""
        # Arrange & Act
        request = ClientContactCreateRequest(
            client_organization_id=1,
            full_name="田中一郎",
            mobile="090-1234-5678",
        )

        # Assert
        assert request.mobile == "090-1234-5678"


class TestClientContactUpdateRequest:
    """顧客担当者更新リクエストのテスト"""

    def test_update_request_partial(self) -> None:
        """正常系：一部のフィールドのみ更新できる"""
        # Arrange & Act
        request = ClientContactUpdateRequest(
            department="企画部",
            position="課長",
        )

        # Assert
        assert request.department == "企画部"
        assert request.position == "課長"
        assert request.full_name is None
        assert request.email is None

    def test_update_request_empty(self) -> None:
        """正常系：フィールドなしでも作成できる（部分更新用）"""
        # Arrange & Act
        request = ClientContactUpdateRequest()

        # Assert
        assert request.full_name is None
        assert request.department is None

    def test_update_request_model_dump_exclude_unset(self) -> None:
        """正常系：exclude_unsetで設定されたフィールドのみ取得できる"""
        # Arrange
        request = ClientContactUpdateRequest(
            position="部長",
            is_primary=True,
        )

        # Act
        data = request.model_dump(exclude_unset=True)

        # Assert
        assert "position" in data
        assert "is_primary" in data
        assert "full_name" not in data
        assert "department" not in data


class TestClientContactResponse:
    """顧客担当者レスポンスのテスト"""

    def test_response_from_entity(self) -> None:
        """正常系：エンティティからレスポンスを作成できる"""
        # Arrange
        from datetime import datetime, timezone

        from src.domain.entities.client_contact_entity import ClientContactEntity

        entity = ClientContactEntity(
            id=1,
            client_organization_id=1,
            full_name="田中一郎",
            department="営業部",
            position="部長",
            email="tanaka@example.com",
            phone="03-1234-5678",
            mobile="090-1234-5678",
            is_primary=True,
            notes="キーパーソン",
            created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            deleted_at=None,
        )

        # Act
        response = ClientContactResponse.model_validate(entity)

        # Assert
        assert response.id == 1
        assert response.client_organization_id == 1
        assert response.full_name == "田中一郎"
        assert response.department == "営業部"
        assert response.position == "部長"
        assert response.email == "tanaka@example.com"
        assert response.phone == "03-1234-5678"
        assert response.mobile == "090-1234-5678"
        assert response.is_primary is True
        assert response.notes == "キーパーソン"
        assert response.deleted_at is None
