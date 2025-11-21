"""
CSVインポートユースケース

CSVファイルのアップロード、バリデーション、インポート実行に関するビジネスロジック。
TDD原則に基づき、テストファーストで実装します。
"""

from datetime import datetime

from src.application.schemas.csv_import import (
    ColumnMappingSchema,
    CsvValidationResponse,
    ImportResultResponse,
    ValidationErrorSchema,
)
from src.domain.entities.csv_import_entity import (
    ColumnMapping,
    ImportStatus,
)
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)
from src.domain.interfaces.csv_import_service import ICsvImportService
from src.domain.interfaces.organization_repository import IOrganizationRepository


class CsvImportUseCase:
    """
    CSVインポートユースケース

    CSVファイルのアップロード、バリデーション、インポート実行を管理します。
    """

    def __init__(
        self,
        csv_import_service: ICsvImportService,
        organization_repository: IOrganizationRepository,
        client_organization_repository: IClientOrganizationRepository,
    ):
        """
        Args:
            csv_import_service: CSVインポートサービス
            organization_repository: 組織リポジトリ
            client_organization_repository: 顧客組織リポジトリ
        """
        self.csv_import_service = csv_import_service
        self.organization_repository = organization_repository
        self.client_organization_repository = client_organization_repository

    def _convert_to_domain_mappings(
        self, schema_mappings: list[ColumnMappingSchema]
    ) -> list[ColumnMapping]:
        """スキーマのマッピングをドメインエンティティに変換"""
        return [
            ColumnMapping(
                csv_column_name=m.csv_column_name,
                system_field_name=m.system_field_name,
                is_required=m.is_required,
            )
            for m in schema_mappings
        ]

    def _convert_validation_errors_to_schema(self, errors: list) -> list[ValidationErrorSchema]:
        """ドメインのバリデーションエラーをスキーマに変換"""
        return [
            ValidationErrorSchema(
                row_number=e.row_number,
                column_name=e.column_name,
                error_message=e.error_message,
                value=e.value,
            )
            for e in errors
        ]

    async def validate_csv_file(
        self,
        file_content: bytes,
        column_mappings: list[ColumnMappingSchema],
        encoding: str = "utf-8",
    ) -> CsvValidationResponse:
        """
        CSVファイルをバリデーションする

        Args:
            file_content: CSVファイルの内容（バイト列）
            column_mappings: カラムマッピングのリスト
            encoding: ファイルエンコーディング

        Returns:
            バリデーション結果

        Raises:
            ValueError: ファイルの解析に失敗した場合
        """
        # カラムマッピングをドメインエンティティに変換
        domain_mappings = self._convert_to_domain_mappings(column_mappings)

        # CSVファイルを解析
        rows = await self.csv_import_service.parse_csv_file(
            file_content=file_content,
            column_mappings=domain_mappings,
            encoding=encoding,
        )

        # 必須フィールドを抽出
        required_fields = [m.system_field_name for m in domain_mappings if m.is_required]

        # バリデーション実行
        result = await self.csv_import_service.validate_csv_data(
            rows=rows,
            required_fields=required_fields,
        )

        # プレビューデータを生成（最初の5行）
        preview_data = [row.data for row in rows[:5]]

        # レスポンスを構築
        return CsvValidationResponse(
            is_valid=not result.has_errors(),
            total_rows=result.total_rows,
            validation_errors=self._convert_validation_errors_to_schema(result.validation_errors),
            preview_data=preview_data,
        )

    async def execute_import(
        self,
        file_content: bytes,
        column_mappings: list[ColumnMappingSchema],
        parent_organization_id: int,
        encoding: str = "utf-8",
        skip_validation: bool = False,
    ) -> ImportResultResponse:
        """
        CSVファイルから顧客組織をインポートする

        Args:
            file_content: CSVファイルの内容（バイト列）
            column_mappings: カラムマッピングのリスト
            parent_organization_id: 親組織ID（営業支援会社のID）
            encoding: ファイルエンコーディング
            skip_validation: バリデーションをスキップするかどうか

        Returns:
            インポート結果

        Raises:
            ValueError: インポート処理に失敗した場合
        """
        started_at = datetime.now()

        # カラムマッピングをドメインエンティティに変換
        domain_mappings = self._convert_to_domain_mappings(column_mappings)

        # CSVファイルを解析
        rows = await self.csv_import_service.parse_csv_file(
            file_content=file_content,
            column_mappings=domain_mappings,
            encoding=encoding,
        )

        # バリデーション（skip_validationがFalseの場合）
        if not skip_validation:
            required_fields = [m.system_field_name for m in domain_mappings if m.is_required]
            validation_result = await self.csv_import_service.validate_csv_data(
                rows=rows,
                required_fields=required_fields,
            )

            # バリデーションエラーがある場合は処理を中断
            if validation_result.has_errors():
                return ImportResultResponse(
                    status=ImportStatus.FAILED.value,
                    total_rows=validation_result.total_rows,
                    successful_rows=0,
                    failed_rows=validation_result.failed_rows,
                    validation_errors=self._convert_validation_errors_to_schema(
                        validation_result.validation_errors
                    ),
                    started_at=started_at,
                    completed_at=datetime.now(),
                    error_summary=validation_result.get_error_summary(),
                )

        # インポート実行
        import_result = await self.csv_import_service.import_organizations(
            rows=rows,
            parent_organization_id=parent_organization_id,
        )

        completed_at = datetime.now()

        # レスポンスを構築
        return ImportResultResponse(
            status=import_result.status.value,
            total_rows=import_result.total_rows,
            successful_rows=import_result.successful_rows,
            failed_rows=import_result.failed_rows,
            validation_errors=self._convert_validation_errors_to_schema(
                import_result.validation_errors
            ),
            started_at=started_at,
            completed_at=completed_at,
            error_summary=import_result.get_error_summary(),
        )

    async def get_csv_template(self) -> dict[str, list[str]]:
        """
        CSVテンプレート情報を取得する

        Returns:
            テンプレート情報（カラム名と必須フィールド）
        """
        # 標準的なフィールドマッピング
        standard_fields = [
            "company_name",  # 会社名（必須）
            "company_url",  # 会社URL（必須）
            "industry",  # 業種
            "employee_count",  # 従業員数
            "annual_revenue",  # 年商
            "established_year",  # 設立年
            "website",  # Webサイト
            "sales_person",  # 担当営業
            "notes",  # 備考
        ]

        required_fields = ["company_name", "company_url"]

        return {
            "columns": standard_fields,
            "required_columns": required_fields,
            "sample_data": [
                {
                    "company_name": "株式会社サンプル",
                    "company_url": "https://example.com",
                    "industry": "IT・ソフトウェア",
                    "employee_count": "100",
                    "annual_revenue": "1000000000",
                    "established_year": "2000",
                    "website": "https://example.com",
                    "sales_person": "山田太郎",
                    "notes": "サンプルデータ",
                }
            ],
        }
