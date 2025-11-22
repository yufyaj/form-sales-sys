"""
CSVインポートAPIの結合テスト

実際のPostgreSQLデータベースを使用してAPIエンドポイントをテストします。
TDD原則に従い、APIの動作を検証します。
"""
import io

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.security import create_access_token
from src.app.main import app
from src.infrastructure.persistence.models import Organization, OrganizationType, User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """テスト用ユーザーを作成"""
    # 営業支援会社組織を作成
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
    )
    db_session.add(org)
    await db_session.flush()

    # ユーザーを作成
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="dummy_hash",
        organization_id=org.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """認証ヘッダーを生成"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_csv_content() -> bytes:
    """サンプルCSVファイルの内容を生成"""
    csv_data = """company_name,company_url,industry,employee_count,annual_revenue
株式会社サンプル1,https://example1.com,IT・ソフトウェア,100,1000000000
株式会社サンプル2,https://example2.com,製造業,200,2000000000
株式会社サンプル3,https://example3.com,サービス業,50,500000000
"""
    return csv_data.encode("utf-8")


@pytest.fixture
def invalid_csv_content() -> bytes:
    """不正なCSVファイルの内容を生成（必須フィールド欠落）"""
    csv_data = """company_name,company_url,industry
,https://example1.com,IT・ソフトウェア
株式会社サンプル2,,製造業
"""
    return csv_data.encode("utf-8")


class TestCsvImportTemplateEndpoint:
    """CSVテンプレートエンドポイントのテスト"""

    @pytest.mark.asyncio
    async def test_get_csv_template_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
    ):
        """CSVテンプレート取得（成功）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/csv-import/template",
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "columns" in data
        assert "required_columns" in data
        assert "sample_data" in data
        assert "company_name" in data["columns"]
        assert "company_url" in data["columns"]
        assert "company_name" in data["required_columns"]
        assert "company_url" in data["required_columns"]

    @pytest.mark.asyncio
    async def test_get_csv_template_unauthorized(self, db_session: AsyncSession):
        """CSVテンプレート取得（未認証）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/csv-import/template")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCsvImportValidateEndpoint:
    """CSVバリデーションエンドポイントのテスト"""

    @pytest.mark.asyncio
    async def test_validate_csv_file_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
        sample_csv_content: bytes,
    ):
        """CSVファイルバリデーション（成功）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(sample_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/validate",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["is_valid"] is True
        assert data["total_rows"] == 3
        assert len(data["validation_errors"]) == 0
        assert len(data["preview_data"]) <= 5

    @pytest.mark.asyncio
    async def test_validate_csv_file_with_validation_errors(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
        invalid_csv_content: bytes,
    ):
        """CSVファイルバリデーション（バリデーションエラー）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(invalid_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/validate",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["is_valid"] is False
        assert data["total_rows"] == 2
        assert len(data["validation_errors"]) > 0

    @pytest.mark.asyncio
    async def test_validate_csv_file_invalid_file_type(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
    ):
        """CSVファイルバリデーション（不正なファイルタイプ）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.txt", io.BytesIO(b"invalid content"), "text/plain")}
            response = await client.post(
                "/api/v1/csv-import/validate",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_validate_csv_file_unauthorized(
        self,
        db_session: AsyncSession,
        sample_csv_content: bytes,
    ):
        """CSVファイルバリデーション（未認証）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(sample_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/validate",
                files=files,
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCsvImportExecuteEndpoint:
    """CSVインポート実行エンドポイントのテスト"""

    @pytest.mark.asyncio
    async def test_execute_csv_import_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
        sample_csv_content: bytes,
    ):
        """CSVインポート実行（成功）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(sample_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/import",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["status"] == "completed"
        assert data["total_rows"] == 3
        assert data["successful_rows"] == 3
        assert data["failed_rows"] == 0
        assert len(data["validation_errors"]) == 0

    @pytest.mark.asyncio
    async def test_execute_csv_import_with_validation_errors(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
        invalid_csv_content: bytes,
    ):
        """CSVインポート実行（バリデーションエラー）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(invalid_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/import",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["status"] == "failed"
        assert data["failed_rows"] > 0
        assert len(data["validation_errors"]) > 0

    @pytest.mark.asyncio
    async def test_execute_csv_import_invalid_file_type(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
    ):
        """CSVインポート実行（不正なファイルタイプ）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.txt", io.BytesIO(b"invalid content"), "text/plain")}
            response = await client.post(
                "/api/v1/csv-import/import",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_execute_csv_import_file_too_large(
        self,
        db_session: AsyncSession,
        test_user: User,
        auth_headers: dict[str, str],
    ):
        """CSVインポート実行（ファイルサイズ超過）"""
        # 10MBを超えるダミーファイル
        large_content = b"a" * (11 * 1024 * 1024)

        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(large_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/import",
                headers=auth_headers,
                files=files,
            )

        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    @pytest.mark.asyncio
    async def test_execute_csv_import_unauthorized(
        self,
        db_session: AsyncSession,
        sample_csv_content: bytes,
    ):
        """CSVインポート実行（未認証）"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("test.csv", io.BytesIO(sample_csv_content), "text/csv")}
            response = await client.post(
                "/api/v1/csv-import/import",
                files=files,
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
