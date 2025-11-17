"""
顧客組織スキーマの単体テスト

Pydantic v2のバリデーション機能をテストします。
"""
import pytest
from pydantic import ValidationError

from src.application.schemas.client_organization import (
    ClientOrganizationCreateRequest,
    ClientOrganizationResponse,
    ClientOrganizationUpdateRequest,
)


class TestClientOrganizationCreateRequest:
    """顧客組織作成リクエストのテスト"""

    def test_create_request_valid(self) -> None:
        """正常系：有効なデータでスキーマを作成できる"""
        # Arrange & Act
        request = ClientOrganizationCreateRequest(
            organization_id=1,
            industry="IT・ソフトウェア",
            employee_count=100,
            annual_revenue=100000000,
            established_year=2010,
            website="https://example.com",
            sales_person="山田太郎",
            notes="重要顧客",
        )

        # Assert
        assert request.organization_id == 1
        assert request.industry == "IT・ソフトウェア"
        assert request.employee_count == 100
        assert request.annual_revenue == 100000000
        assert request.established_year == 2010
        assert request.website == "https://example.com"
        assert request.sales_person == "山田太郎"
        assert request.notes == "重要顧客"

    def test_create_request_minimal(self) -> None:
        """正常系：必須項目のみでスキーマを作成できる"""
        # Arrange & Act
        request = ClientOrganizationCreateRequest(organization_id=1)

        # Assert
        assert request.organization_id == 1
        assert request.industry is None
        assert request.employee_count is None

    def test_create_request_invalid_employee_count_negative(self) -> None:
        """異常系：従業員数が負の値の場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientOrganizationCreateRequest(
                organization_id=1,
                employee_count=-1,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_count",) for error in errors)

    def test_create_request_invalid_annual_revenue_negative(self) -> None:
        """異常系：年商が負の値の場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientOrganizationCreateRequest(
                organization_id=1,
                annual_revenue=-1,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("annual_revenue",) for error in errors)

    def test_create_request_invalid_established_year_too_old(self) -> None:
        """異常系：設立年が1800年未満の場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientOrganizationCreateRequest(
                organization_id=1,
                established_year=1799,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("established_year",) for error in errors)

    def test_create_request_invalid_established_year_too_new(self) -> None:
        """異常系：設立年が2100年を超える場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientOrganizationCreateRequest(
                organization_id=1,
                established_year=2101,
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("established_year",) for error in errors)

    def test_create_request_invalid_website_no_protocol(self) -> None:
        """異常系：WebサイトURLにプロトコルがない場合はエラー"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClientOrganizationCreateRequest(
                organization_id=1,
                website="example.com",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("website",) for error in errors)
        assert any(
            "http://またはhttps://で始まる必要があります" in str(error["ctx"])
            for error in errors
        )

    def test_create_request_valid_website_http(self) -> None:
        """正常系：http://で始まるURLは有効"""
        # Arrange & Act
        request = ClientOrganizationCreateRequest(
            organization_id=1,
            website="http://example.com",
        )

        # Assert
        assert request.website == "http://example.com"

    def test_create_request_valid_website_https(self) -> None:
        """正常系：https://で始まるURLは有効"""
        # Arrange & Act
        request = ClientOrganizationCreateRequest(
            organization_id=1,
            website="https://example.com",
        )

        # Assert
        assert request.website == "https://example.com"


class TestClientOrganizationUpdateRequest:
    """顧客組織更新リクエストのテスト"""

    def test_update_request_partial(self) -> None:
        """正常系：一部のフィールドのみ更新できる"""
        # Arrange & Act
        request = ClientOrganizationUpdateRequest(
            industry="製造業",
            employee_count=500,
        )

        # Assert
        assert request.industry == "製造業"
        assert request.employee_count == 500
        assert request.annual_revenue is None
        assert request.website is None

    def test_update_request_empty(self) -> None:
        """正常系：フィールドなしでも作成できる（部分更新用）"""
        # Arrange & Act
        request = ClientOrganizationUpdateRequest()

        # Assert
        assert request.industry is None
        assert request.employee_count is None

    def test_update_request_model_dump_exclude_unset(self) -> None:
        """正常系：exclude_unsetで設定されたフィールドのみ取得できる"""
        # Arrange
        request = ClientOrganizationUpdateRequest(
            industry="小売業",
            notes="更新",
        )

        # Act
        data = request.model_dump(exclude_unset=True)

        # Assert
        assert "industry" in data
        assert "notes" in data
        assert "employee_count" not in data
        assert "annual_revenue" not in data


class TestClientOrganizationResponse:
    """顧客組織レスポンスのテスト"""

    def test_response_from_entity(self) -> None:
        """正常系：エンティティからレスポンスを作成できる"""
        # Arrange
        from datetime import datetime, timezone

        from src.domain.entities.client_organization_entity import (
            ClientOrganizationEntity,
        )

        entity = ClientOrganizationEntity(
            id=1,
            organization_id=100,
            industry="IT・ソフトウェア",
            employee_count=100,
            annual_revenue=100000000,
            established_year=2010,
            website="https://example.com",
            sales_person="山田太郎",
            notes="重要顧客",
            created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            deleted_at=None,
        )

        # Act
        response = ClientOrganizationResponse.model_validate(entity)

        # Assert
        assert response.id == 1
        assert response.organization_id == 100
        assert response.industry == "IT・ソフトウェア"
        assert response.employee_count == 100
        assert response.annual_revenue == 100000000
        assert response.established_year == 2010
        assert response.website == "https://example.com"
        assert response.sales_person == "山田太郎"
        assert response.notes == "重要顧客"
        assert response.deleted_at is None
