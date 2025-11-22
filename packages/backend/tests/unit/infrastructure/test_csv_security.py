"""
CSVインポートのセキュリティテスト

CSVインジェクション、ファイル検証、DoS対策のテスト
"""

import io

import pytest

from src.domain.entities.csv_import_entity import ColumnMapping
from src.infrastructure.services.csv_import_service import CsvImportService


class TestCsvInjectionPrevention:
    """CSVインジェクション対策のテスト"""

    @pytest.mark.asyncio
    async def test_reject_formula_injection_equals(self, db_session):
        """数式インジェクション対策（=で始まる値）"""
        csv_service = CsvImportService(db_session)

        csv_content = b"""company_name,company_url
=1+1,https://example.com"""

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "セキュリティ上の理由により" in str(exc_info.value)
        assert "'='" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reject_formula_injection_plus(self, db_session):
        """数式インジェクション対策（+で始まる値）"""
        csv_service = CsvImportService(db_session)

        csv_content = b"""company_name,company_url
+cmd|'/c calc'!A1,https://example.com"""

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "セキュリティ上の理由により" in str(exc_info.value)
        assert "'+'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reject_formula_injection_minus(self, db_session):
        """数式インジェクション対策（-で始まる値）"""
        csv_service = CsvImportService(db_session)

        csv_content = b"""company_name,company_url
-2+5,https://example.com"""

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "セキュリティ上の理由により" in str(exc_info.value)
        assert "'-'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reject_formula_injection_at(self, db_session):
        """数式インジェクション対策（@で始まる値）"""
        csv_service = CsvImportService(db_session)

        csv_content = b"""company_name,company_url
@SUM(A1:A10),https://example.com"""

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "セキュリティ上の理由により" in str(exc_info.value)
        assert "'@'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_accept_safe_values(self, db_session):
        """安全な値は正常に処理される"""
        csv_service = CsvImportService(db_session)

        csv_content = b"""company_name,company_url
Sample Company,https://example.com"""

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        rows = await csv_service.parse_csv_file(csv_content, column_mappings)

        assert len(rows) == 1
        assert rows[0].get_value("company_name") == "Sample Company"
        assert rows[0].get_value("company_url") == "https://example.com"


class TestDoSPrevention:
    """DoS攻撃対策のテスト"""

    @pytest.mark.asyncio
    async def test_reject_too_many_rows(self, db_session):
        """行数制限のテスト"""
        csv_service = CsvImportService(db_session)

        # 最大行数を超えるCSVを生成
        max_rows = CsvImportService.MAX_CSV_ROWS
        csv_lines = ["company_name,company_url"]
        for i in range(max_rows + 1):
            csv_lines.append(f"Company{i},https://example{i}.com")

        csv_content = "\n".join(csv_lines).encode("utf-8")

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "行数が上限" in str(exc_info.value)
        assert str(max_rows) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reject_too_long_cell(self, db_session):
        """セル長制限のテスト"""
        csv_service = CsvImportService(db_session)

        # 最大文字数を超える値を生成
        max_length = CsvImportService.MAX_CELL_LENGTH
        long_value = "A" * (max_length + 1)

        csv_content = f"""company_name,company_url
{long_value},https://example.com""".encode(
            "utf-8"
        )

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        with pytest.raises(ValueError) as exc_info:
            await csv_service.parse_csv_file(csv_content, column_mappings)

        assert "セルの文字数が上限" in str(exc_info.value)
        assert str(max_length) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_accept_within_limits(self, db_session):
        """制限内のデータは正常に処理される"""
        csv_service = CsvImportService(db_session)

        # 制限内のデータ（100行）
        csv_lines = ["company_name,company_url"]
        for i in range(100):
            csv_lines.append(f"Company{i},https://example{i}.com")

        csv_content = "\n".join(csv_lines).encode("utf-8")

        column_mappings = [
            ColumnMapping(csv_column_name="company_name", system_field_name="company_name"),
            ColumnMapping(csv_column_name="company_url", system_field_name="company_url"),
        ]

        rows = await csv_service.parse_csv_file(csv_content, column_mappings)

        assert len(rows) == 100
