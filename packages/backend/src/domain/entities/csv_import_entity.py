"""
CSVインポートエンティティ

CSVファイルからのデータインポートに関するドメインモデル。
カラムマッピング、バリデーション、インポート結果を管理します。
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum as PyEnum


class ImportStatus(str, PyEnum):
    """インポートステータス"""

    PENDING = "pending"  # 処理待ち
    PROCESSING = "processing"  # 処理中
    COMPLETED = "completed"  # 完了
    FAILED = "failed"  # 失敗


@dataclass
class ColumnMapping:
    """
    カラムマッピング

    CSVファイルのカラムとシステムフィールドのマッピングを定義します。
    """

    csv_column_name: str  # CSVファイル内のカラム名
    system_field_name: str  # システム内のフィールド名
    is_required: bool = False  # 必須フィールドかどうか

    def validate(self) -> bool:
        """マッピングの妥当性を検証"""
        return bool(self.csv_column_name and self.system_field_name)


@dataclass
class ValidationError:
    """
    バリデーションエラー

    CSVデータのバリデーション時に発生したエラーを表現します。
    """

    row_number: int  # 行番号（1始まり）
    column_name: str  # カラム名
    error_message: str  # エラーメッセージ
    value: str | None = None  # エラーが発生した値


@dataclass
class ImportResult:
    """
    インポート結果

    CSVインポート処理の結果を表現します。
    """

    total_rows: int  # 総行数
    successful_rows: int  # 成功行数
    failed_rows: int  # 失敗行数
    validation_errors: list[ValidationError]  # バリデーションエラーのリスト
    status: ImportStatus  # インポートステータス
    started_at: datetime | None = None  # 開始時刻
    completed_at: datetime | None = None  # 完了時刻

    def is_successful(self) -> bool:
        """インポートが成功したかを判定"""
        return self.status == ImportStatus.COMPLETED and self.failed_rows == 0

    def has_errors(self) -> bool:
        """エラーが存在するかを判定"""
        return len(self.validation_errors) > 0 or self.failed_rows > 0

    def get_error_summary(self) -> str:
        """エラーサマリーを取得"""
        if not self.has_errors():
            return "エラーはありません"

        error_count = len(self.validation_errors)
        return f"バリデーションエラー: {error_count}件, 失敗行数: {self.failed_rows}件"


@dataclass
class CsvRowData:
    """
    CSV行データ

    CSVファイルの1行分のデータを表現します。
    カラムマッピングに基づいて変換された値を保持します。
    """

    row_number: int  # 行番号（1始まり）
    data: dict[str, str | None]  # フィールド名とその値のマッピング

    def get_value(self, field_name: str) -> str | None:
        """指定されたフィールドの値を取得"""
        return self.data.get(field_name)

    def has_required_fields(self, required_fields: list[str]) -> bool:
        """必須フィールドが全て存在するかを検証"""
        for field in required_fields:
            value = self.get_value(field)
            if not value or not value.strip():
                return False
        return True

    def validate_required_fields(self, required_fields: list[str]) -> list[ValidationError]:
        """必須フィールドのバリデーション"""
        errors = []
        for field in required_fields:
            value = self.get_value(field)
            if not value or not value.strip():
                errors.append(
                    ValidationError(
                        row_number=self.row_number,
                        column_name=field,
                        error_message=f"{field}は必須項目です",
                        value=value,
                    )
                )
        return errors
