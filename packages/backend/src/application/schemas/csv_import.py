"""
CSVインポートスキーマ

API送受信用のDTOモデル。
FastAPIのPydanticモデルでバリデーションを行います。
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ColumnMappingSchema(BaseModel):
    """カラムマッピングスキーマ"""

    csv_column_name: str = Field(
        ..., min_length=1, max_length=255, description="CSVファイル内のカラム名"
    )
    system_field_name: str = Field(
        ..., min_length=1, max_length=255, description="システム内のフィールド名"
    )
    is_required: bool = Field(default=False, description="必須フィールドかどうか")

    @field_validator("csv_column_name", "system_field_name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """空文字列でないことを検証"""
        if not v.strip():
            raise ValueError("空文字列は許可されていません")
        return v.strip()


class CsvUploadRequest(BaseModel):
    """CSVアップロードリクエスト"""

    column_mappings: list[ColumnMappingSchema] = Field(
        ..., min_length=1, description="カラムマッピングのリスト"
    )
    encoding: str = Field(default="utf-8", description="ファイルエンコーディング")

    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, v: str) -> str:
        """サポートされているエンコーディングかを検証"""
        supported_encodings = ["utf-8", "shift_jis", "cp932", "euc-jp"]
        if v.lower() not in supported_encodings:
            raise ValueError(
                f"サポートされていないエンコーディングです。サポート: {', '.join(supported_encodings)}"
            )
        return v.lower()


class ValidationErrorSchema(BaseModel):
    """バリデーションエラースキーマ"""

    row_number: int = Field(..., ge=1, description="行番号（1始まり）")
    column_name: str = Field(..., description="カラム名")
    error_message: str = Field(..., description="エラーメッセージ")
    value: str | None = Field(default=None, description="エラーが発生した値")


class CsvValidationResponse(BaseModel):
    """CSVバリデーションレスポンス"""

    is_valid: bool = Field(..., description="バリデーションが成功したかどうか")
    total_rows: int = Field(..., ge=0, description="総行数")
    validation_errors: list[ValidationErrorSchema] = Field(
        default_factory=list, description="バリデーションエラーのリスト"
    )
    preview_data: list[dict[str, str | None]] = Field(
        default_factory=list, description="プレビューデータ（最初の5行）"
    )


class ImportExecuteRequest(BaseModel):
    """インポート実行リクエスト"""

    column_mappings: list[ColumnMappingSchema] = Field(
        ..., min_length=1, description="カラムマッピングのリスト"
    )
    encoding: str = Field(default="utf-8", description="ファイルエンコーディング")
    skip_validation: bool = Field(default=False, description="バリデーションをスキップするかどうか")


class ImportResultResponse(BaseModel):
    """インポート結果レスポンス"""

    status: str = Field(..., description="インポートステータス")
    total_rows: int = Field(..., ge=0, description="総行数")
    successful_rows: int = Field(..., ge=0, description="成功行数")
    failed_rows: int = Field(..., ge=0, description="失敗行数")
    validation_errors: list[ValidationErrorSchema] = Field(
        default_factory=list, description="バリデーションエラーのリスト"
    )
    started_at: datetime | None = Field(default=None, description="開始時刻")
    completed_at: datetime | None = Field(default=None, description="完了時刻")
    error_summary: str = Field(default="", description="エラーサマリー")


class CsvTemplateResponse(BaseModel):
    """CSVテンプレートレスポンス"""

    columns: list[str] = Field(..., description="カラム名のリスト")
    required_columns: list[str] = Field(..., description="必須カラムのリスト")
    sample_data: list[dict[str, str]] = Field(default_factory=list, description="サンプルデータ")
    description: str = Field(default="", description="テンプレートの説明")
