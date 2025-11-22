"""
CSVインポートエンティティの単体テスト

TDD原則に従い、ドメインエンティティのビジネスロジックをテストします。
"""
from datetime import datetime

import pytest

from src.domain.entities.csv_import_entity import (
    ColumnMapping,
    CsvRowData,
    ImportResult,
    ImportStatus,
    ValidationError,
)


class TestColumnMapping:
    """ColumnMappingエンティティのテスト"""

    def test_column_mapping_creation(self):
        """カラムマッピングの作成テスト"""
        mapping = ColumnMapping(
            csv_column_name="会社名",
            system_field_name="company_name",
            is_required=True,
        )

        assert mapping.csv_column_name == "会社名"
        assert mapping.system_field_name == "company_name"
        assert mapping.is_required is True

    def test_column_mapping_validation_success(self):
        """カラムマッピングの妥当性検証（成功）"""
        mapping = ColumnMapping(
            csv_column_name="会社名",
            system_field_name="company_name",
        )

        assert mapping.validate() is True

    def test_column_mapping_validation_failure_empty_csv_column(self):
        """カラムマッピングの妥当性検証（CSVカラム名が空）"""
        mapping = ColumnMapping(
            csv_column_name="",
            system_field_name="company_name",
        )

        assert mapping.validate() is False

    def test_column_mapping_validation_failure_empty_system_field(self):
        """カラムマッピングの妥当性検証（システムフィールド名が空）"""
        mapping = ColumnMapping(
            csv_column_name="会社名",
            system_field_name="",
        )

        assert mapping.validate() is False


class TestValidationError:
    """ValidationErrorエンティティのテスト"""

    def test_validation_error_creation(self):
        """バリデーションエラーの作成テスト"""
        error = ValidationError(
            row_number=2,
            column_name="company_name",
            error_message="会社名は必須です",
            value=None,
        )

        assert error.row_number == 2
        assert error.column_name == "company_name"
        assert error.error_message == "会社名は必須です"
        assert error.value is None

    def test_validation_error_with_value(self):
        """バリデーションエラー（値付き）の作成テスト"""
        error = ValidationError(
            row_number=3,
            column_name="employee_count",
            error_message="従業員数は数値である必要があります",
            value="abc",
        )

        assert error.row_number == 3
        assert error.column_name == "employee_count"
        assert error.error_message == "従業員数は数値である必要があります"
        assert error.value == "abc"


class TestImportResult:
    """ImportResultエンティティのテスト"""

    def test_import_result_creation(self):
        """インポート結果の作成テスト"""
        result = ImportResult(
            total_rows=10,
            successful_rows=8,
            failed_rows=2,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        assert result.total_rows == 10
        assert result.successful_rows == 8
        assert result.failed_rows == 2
        assert len(result.validation_errors) == 0
        assert result.status == ImportStatus.COMPLETED

    def test_import_result_is_successful_true(self):
        """インポート成功判定（成功）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=10,
            failed_rows=0,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        assert result.is_successful() is True

    def test_import_result_is_successful_false_with_failed_rows(self):
        """インポート成功判定（失敗行あり）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=8,
            failed_rows=2,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        assert result.is_successful() is False

    def test_import_result_is_successful_false_with_failed_status(self):
        """インポート成功判定（ステータスが失敗）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=0,
            failed_rows=10,
            validation_errors=[],
            status=ImportStatus.FAILED,
        )

        assert result.is_successful() is False

    def test_import_result_has_errors_true_with_validation_errors(self):
        """エラー存在判定（バリデーションエラーあり）"""
        errors = [
            ValidationError(
                row_number=2,
                column_name="company_name",
                error_message="会社名は必須です",
            )
        ]
        result = ImportResult(
            total_rows=10,
            successful_rows=9,
            failed_rows=1,
            validation_errors=errors,
            status=ImportStatus.FAILED,
        )

        assert result.has_errors() is True

    def test_import_result_has_errors_true_with_failed_rows(self):
        """エラー存在判定（失敗行あり）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=8,
            failed_rows=2,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        assert result.has_errors() is True

    def test_import_result_has_errors_false(self):
        """エラー存在判定（エラーなし）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=10,
            failed_rows=0,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        assert result.has_errors() is False

    def test_import_result_get_error_summary_no_errors(self):
        """エラーサマリー取得（エラーなし）"""
        result = ImportResult(
            total_rows=10,
            successful_rows=10,
            failed_rows=0,
            validation_errors=[],
            status=ImportStatus.COMPLETED,
        )

        summary = result.get_error_summary()
        assert summary == "エラーはありません"

    def test_import_result_get_error_summary_with_errors(self):
        """エラーサマリー取得（エラーあり）"""
        errors = [
            ValidationError(
                row_number=2,
                column_name="company_name",
                error_message="会社名は必須です",
            ),
            ValidationError(
                row_number=3,
                column_name="company_url",
                error_message="会社URLは必須です",
            ),
        ]
        result = ImportResult(
            total_rows=10,
            successful_rows=7,
            failed_rows=3,
            validation_errors=errors,
            status=ImportStatus.FAILED,
        )

        summary = result.get_error_summary()
        assert "バリデーションエラー: 2件" in summary
        assert "失敗行数: 3件" in summary


class TestCsvRowData:
    """CsvRowDataエンティティのテスト"""

    def test_csv_row_data_creation(self):
        """CSV行データの作成テスト"""
        data = {
            "company_name": "株式会社サンプル",
            "company_url": "https://example.com",
            "industry": "IT",
        }
        row = CsvRowData(row_number=2, data=data)

        assert row.row_number == 2
        assert row.data == data

    def test_csv_row_data_get_value(self):
        """値取得テスト"""
        data = {
            "company_name": "株式会社サンプル",
            "company_url": "https://example.com",
        }
        row = CsvRowData(row_number=2, data=data)

        assert row.get_value("company_name") == "株式会社サンプル"
        assert row.get_value("company_url") == "https://example.com"
        assert row.get_value("nonexistent") is None

    def test_csv_row_data_has_required_fields_true(self):
        """必須フィールド存在チェック（全て存在）"""
        data = {
            "company_name": "株式会社サンプル",
            "company_url": "https://example.com",
        }
        row = CsvRowData(row_number=2, data=data)

        required_fields = ["company_name", "company_url"]
        assert row.has_required_fields(required_fields) is True

    def test_csv_row_data_has_required_fields_false_missing_field(self):
        """必須フィールド存在チェック（フィールド欠落）"""
        data = {
            "company_name": "株式会社サンプル",
        }
        row = CsvRowData(row_number=2, data=data)

        required_fields = ["company_name", "company_url"]
        assert row.has_required_fields(required_fields) is False

    def test_csv_row_data_has_required_fields_false_empty_value(self):
        """必須フィールド存在チェック（値が空）"""
        data = {
            "company_name": "株式会社サンプル",
            "company_url": "",
        }
        row = CsvRowData(row_number=2, data=data)

        required_fields = ["company_name", "company_url"]
        assert row.has_required_fields(required_fields) is False

    def test_csv_row_data_validate_required_fields_success(self):
        """必須フィールドバリデーション（成功）"""
        data = {
            "company_name": "株式会社サンプル",
            "company_url": "https://example.com",
        }
        row = CsvRowData(row_number=2, data=data)

        required_fields = ["company_name", "company_url"]
        errors = row.validate_required_fields(required_fields)

        assert len(errors) == 0

    def test_csv_row_data_validate_required_fields_failure(self):
        """必須フィールドバリデーション（失敗）"""
        data = {
            "company_name": "",
            "company_url": None,
        }
        row = CsvRowData(row_number=2, data=data)

        required_fields = ["company_name", "company_url"]
        errors = row.validate_required_fields(required_fields)

        assert len(errors) == 2
        assert errors[0].row_number == 2
        assert errors[0].column_name == "company_name"
        assert errors[1].column_name == "company_url"
