"""
CSVインポートサービスインターフェース

CSVファイルの解析とインポート処理を行うサービスの抽象化。
依存性逆転の原則に従い、ドメイン層がインフラストラクチャ層に依存しないようにします。
"""

from abc import ABC, abstractmethod

from src.domain.entities.csv_import_entity import (
    ColumnMapping,
    CsvRowData,
    ImportResult,
)


class ICsvImportService(ABC):
    """
    CSVインポートサービスインターフェース

    CSVファイルの解析、バリデーション、インポート処理を定義します。
    """

    @abstractmethod
    async def parse_csv_file(
        self,
        file_content: bytes,
        column_mappings: list[ColumnMapping],
        encoding: str = "utf-8",
    ) -> list[CsvRowData]:
        """
        CSVファイルを解析して行データのリストを返す

        Args:
            file_content: CSVファイルの内容（バイト列）
            column_mappings: カラムマッピングのリスト
            encoding: ファイルエンコーディング

        Returns:
            解析されたCSV行データのリスト

        Raises:
            ValueError: ファイルの解析に失敗した場合
        """
        pass

    @abstractmethod
    async def validate_csv_data(
        self,
        rows: list[CsvRowData],
        required_fields: list[str],
    ) -> ImportResult:
        """
        CSV行データをバリデーションする

        Args:
            rows: CSV行データのリスト
            required_fields: 必須フィールドのリスト

        Returns:
            バリデーション結果を含むImportResult
        """
        pass

    @abstractmethod
    async def import_organizations(
        self,
        rows: list[CsvRowData],
        parent_organization_id: int,
    ) -> ImportResult:
        """
        CSV行データから顧客組織をインポートする

        Args:
            rows: CSV行データのリスト
            parent_organization_id: 親組織ID（営業支援会社のID）

        Returns:
            インポート結果

        Raises:
            ValueError: インポート処理に失敗した場合
        """
        pass
