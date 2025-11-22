"""
CSVインポートサービス実装

CSVファイルの解析とインポート処理を行うサービスの実装。
標準ライブラリのcsvモジュールを使用します。
"""

import csv
import io
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.csv_import_entity import (
    ColumnMapping,
    CsvRowData,
    ImportResult,
    ImportStatus,
    ValidationError,
)
from src.domain.interfaces.csv_import_service import ICsvImportService
from src.infrastructure.persistence.models.client_organization import (
    ClientOrganization,
)
from src.infrastructure.persistence.models.organization import (
    Organization,
    OrganizationType,
)


class CsvImportService(ICsvImportService):
    """
    CSVインポートサービス実装

    標準ライブラリのcsvモジュールを使用してCSVファイルを解析します。
    セキュリティ: CSVインジェクション対策として、特殊文字で始まる値を拒否します。
    """

    # CSVインジェクション対策: 危険な文字で始まるセルを検出
    DANGEROUS_PREFIXES = ["=", "+", "-", "@", "\t", "\r"]

    # DoS対策: CSVファイルの制限
    MAX_CSV_ROWS = 10000  # 最大行数
    MAX_CELL_LENGTH = 10000  # セルの最大文字数

    def __init__(self, db_session: AsyncSession):
        """
        Args:
            db_session: データベースセッション
        """
        self.db_session = db_session

    def _sanitize_csv_value(self, value: str | None) -> str | None:
        """
        CSV値をサニタイズする（CSVインジェクション対策強化版）

        危険な文字で始まる値は完全に拒否します。
        エスケープではなく拒否方式を採用することで、より高いセキュリティを確保します。

        Args:
            value: サニタイズする値

        Returns:
            サニタイズされた値

        Raises:
            ValueError: 危険な文字で始まる値が検出された場合
        """
        if not value:
            return value

        # 空白のみの値はNoneを返す
        stripped_value = value.strip()
        if not stripped_value:
            return None

        # 危険な文字で始まる場合、値を拒否（セキュリティ強化）
        if stripped_value[0] in self.DANGEROUS_PREFIXES:
            raise ValueError(
                f"セキュリティ上の理由により、'{stripped_value[0]}'で始まる値は許可されていません。"
                f"該当値: '{stripped_value[:50]}...'"
            )

        return stripped_value

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
        try:
            # バイト列を文字列にデコード
            text_content = file_content.decode(encoding)
        except UnicodeDecodeError as e:
            raise ValueError(
                f"ファイルのデコードに失敗しました。エンコーディング: {encoding}"
            ) from e

        # CSVマッピング辞書を作成（CSVカラム名 -> システムフィールド名）
        mapping_dict = {m.csv_column_name: m.system_field_name for m in column_mappings}

        rows: list[CsvRowData] = []

        try:
            # StringIOを使用してCSVを解析
            csv_file = io.StringIO(text_content)
            csv_reader = csv.DictReader(csv_file)

            # ヘッダーの検証
            if not csv_reader.fieldnames:
                raise ValueError("CSVファイルにヘッダー行が存在しません")

            # 各行を解析
            for row_num, row in enumerate(csv_reader, start=2):  # ヘッダーが1行目なので2から
                # 行数制限チェック（DoS対策）
                if len(rows) >= self.MAX_CSV_ROWS:
                    raise ValueError(
                        f"CSVファイルの行数が上限（{self.MAX_CSV_ROWS}行）を超えています"
                    )

                # カラムマッピングに基づいてデータを変換
                mapped_data: dict[str, str | None] = {}

                for csv_col, system_field in mapping_dict.items():
                    value = row.get(csv_col)

                    # セル長制限チェック（DoS対策）
                    if value and len(value) > self.MAX_CELL_LENGTH:
                        raise ValueError(
                            f"行{row_num}: セルの文字数が上限（{self.MAX_CELL_LENGTH}文字）を超えています"
                        )

                    # サニタイズ処理（CSVインジェクション対策）
                    sanitized_value = self._sanitize_csv_value(value) if value else None
                    mapped_data[system_field] = sanitized_value

                # CsvRowDataエンティティを作成
                csv_row = CsvRowData(row_number=row_num, data=mapped_data)
                rows.append(csv_row)

        except csv.Error as e:
            raise ValueError(f"CSVファイルの解析に失敗しました: {str(e)}") from e

        if not rows:
            raise ValueError("CSVファイルにデータ行が存在しません")

        return rows

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
        validation_errors: list[ValidationError] = []
        successful_count = 0
        failed_count = 0

        for row in rows:
            # 必須フィールドのバリデーション
            row_errors = row.validate_required_fields(required_fields)

            if row_errors:
                validation_errors.extend(row_errors)
                failed_count += 1
            else:
                successful_count += 1

        # バリデーション結果を構築
        status = ImportStatus.COMPLETED if failed_count == 0 else ImportStatus.FAILED

        return ImportResult(
            total_rows=len(rows),
            successful_rows=successful_count,
            failed_rows=failed_count,
            validation_errors=validation_errors,
            status=status,
        )

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
        started_at = datetime.now()
        validation_errors: list[ValidationError] = []
        successful_count = 0
        failed_count = 0

        try:
            for row in rows:
                try:
                    # 会社名と会社URL（必須フィールド）を取得
                    company_name = row.get_value("company_name")
                    company_url = row.get_value("company_url")

                    if not company_name or not company_url:
                        validation_errors.append(
                            ValidationError(
                                row_number=row.row_number,
                                column_name="company_name/company_url",
                                error_message="会社名と会社URLは必須です",
                                value=None,
                            )
                        )
                        failed_count += 1
                        continue

                    # Organizationエンティティを作成
                    organization = Organization(
                        name=company_name,
                        type=OrganizationType.CLIENT,
                        parent_organization_id=parent_organization_id,
                        email=row.get_value("email"),
                        phone=row.get_value("phone"),
                        address=row.get_value("address"),
                        description=row.get_value("notes"),
                    )

                    self.db_session.add(organization)
                    await self.db_session.flush()  # IDを取得するためにflush

                    # ClientOrganizationエンティティを作成
                    client_org = ClientOrganization(
                        organization_id=organization.id,
                        industry=row.get_value("industry"),
                        employee_count=(
                            int(row.get_value("employee_count"))
                            if row.get_value("employee_count")
                            else None
                        ),
                        annual_revenue=(
                            int(row.get_value("annual_revenue"))
                            if row.get_value("annual_revenue")
                            else None
                        ),
                        established_year=(
                            int(row.get_value("established_year"))
                            if row.get_value("established_year")
                            else None
                        ),
                        website=company_url,
                        sales_person=row.get_value("sales_person"),
                        notes=row.get_value("notes"),
                    )

                    self.db_session.add(client_org)
                    successful_count += 1

                except ValueError as e:
                    validation_errors.append(
                        ValidationError(
                            row_number=row.row_number,
                            column_name="",
                            error_message=f"データ型エラー: {str(e)}",
                            value=None,
                        )
                    )
                    failed_count += 1
                    # ロールバックして次の行へ
                    await self.db_session.rollback()
                    continue

            # コミット
            await self.db_session.commit()

        except Exception as e:
            await self.db_session.rollback()
            raise ValueError(f"インポート処理中にエラーが発生しました: {str(e)}") from e

        completed_at = datetime.now()

        # インポート結果を構築
        status = ImportStatus.COMPLETED if failed_count == 0 else ImportStatus.FAILED

        return ImportResult(
            total_rows=len(rows),
            successful_rows=successful_count,
            failed_rows=failed_count,
            validation_errors=validation_errors,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
        )
