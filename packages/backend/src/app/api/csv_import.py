"""
CSVインポートAPI

顧客組織のCSVインポート機能を提供するAPIエンドポイント。
- CSVアップロード
- カラムマッピング
- バリデーション
- インポート実行
"""

import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.csv_import import (
    ColumnMappingSchema,
    CsvTemplateResponse,
    CsvValidationResponse,
    ImportExecuteRequest,
    ImportResultResponse,
)
from src.application.use_cases.csv_import_use_cases import CsvImportUseCase
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.client_organization_repository import (
    ClientOrganizationRepository,
)
from src.infrastructure.persistence.repositories.organization_repository import (
    OrganizationRepository,
)
from src.infrastructure.services.csv_import_service import CsvImportService

# ロガー設定
logger = logging.getLogger(__name__)

# ルーター作成
router = APIRouter(
    prefix="/csv-import",
    tags=["CSV Import"],
)

# セキュリティ定数
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = ["text/csv", "application/csv", "text/plain"]
# 危険なファイルシグネチャ（マジックナンバー）
DANGEROUS_FILE_SIGNATURES = [
    b"\x4D\x5A",  # PE/EXE (MZ)
    b"\x7F\x45\x4C\x46",  # ELF
    b"\x50\x4B\x03\x04",  # ZIP/JAR
    b"\x25\x50\x44\x46",  # PDF
    b"\x89\x50\x4E\x47",  # PNG
    b"\xFF\xD8\xFF",  # JPEG
    b"\x47\x49\x46",  # GIF
]


def validate_csv_file_extension(filename: str) -> bool:
    """
    CSVファイル拡張子を厳格に検証

    Args:
        filename: 検証するファイル名

    Returns:
        有効な場合True、そうでない場合False
    """
    if not filename:
        return False

    # NULLバイト除去（NULLバイトインジェクション対策）
    filename = filename.replace("\x00", "")

    # 拡張子を小文字で検証
    ext = Path(filename).suffix.lower()

    # 許可リストによる検証（ホワイトリスト方式）
    return ext == ".csv"


def validate_file_content_type(content_type: str | None) -> bool:
    """
    ファイルのContent-Typeを検証

    Args:
        content_type: 検証するContent-Type

    Returns:
        有効な場合True、そうでない場合False
    """
    if not content_type:
        return False

    # Content-Typeを小文字で正規化
    content_type = content_type.lower().strip()

    # セミコロン以降のパラメータを除去（例: "text/csv; charset=utf-8" -> "text/csv"）
    if ";" in content_type:
        content_type = content_type.split(";")[0].strip()

    return content_type in ALLOWED_CONTENT_TYPES


def validate_file_magic_number(file_content: bytes) -> bool:
    """
    ファイル内容のマジックナンバーを検証（バイナリファイル検出）

    Args:
        file_content: 検証するファイル内容

    Returns:
        安全な場合True、危険なファイルの場合False
    """
    if not file_content:
        return True

    # 危険なファイルシグネチャをチェック
    for signature in DANGEROUS_FILE_SIGNATURES:
        if file_content.startswith(signature):
            return False

    return True


def validate_csv_file_security(file: UploadFile, file_content: bytes) -> None:
    """
    CSVファイルのセキュリティ検証を一括実行

    Args:
        file: アップロードされたファイル
        file_content: ファイルの内容

    Raises:
        HTTPException: 検証に失敗した場合
    """
    # 1. ファイル拡張子の検証
    if not validate_csv_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイル（.csv拡張子）のみアップロード可能です",
        )

    # 2. Content-Typeの検証
    if not validate_file_content_type(file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていないContent-Typeです。許可: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # 3. ファイルサイズの検証
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ファイルサイズが大きすぎます（最大{MAX_FILE_SIZE // (1024 * 1024)}MB）",
        )

    # 4. マジックナンバーの検証（バイナリファイル検出）
    if not validate_file_magic_number(file_content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルとして無効なファイル形式です",
        )


async def get_csv_import_use_case(
    session: AsyncSession = Depends(get_db),
) -> CsvImportUseCase:
    """
    CSVインポートユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        CsvImportUseCaseインスタンス
    """
    # サービスとリポジトリをインスタンス化
    csv_service = CsvImportService(session)
    org_repo = OrganizationRepository(session)
    client_org_repo = ClientOrganizationRepository(session)

    # ユースケースをインスタンス化
    return CsvImportUseCase(
        csv_import_service=csv_service,
        organization_repository=org_repo,
        client_organization_repository=client_org_repo,
    )


@router.get(
    "/template",
    response_model=CsvTemplateResponse,
    summary="CSVテンプレート取得",
    description="顧客組織インポート用のCSVテンプレート情報を取得します",
)
async def get_csv_template(
    current_user: UserEntity = Depends(get_current_active_user),
    use_case: CsvImportUseCase = Depends(get_csv_import_use_case),
) -> CsvTemplateResponse:
    """
    CSVテンプレート情報を取得

    Returns:
        CSVテンプレート情報（カラム名、必須フィールド、サンプルデータ）

    Raises:
        HTTPException: エラーが発生した場合
    """
    try:
        template_data = await use_case.get_csv_template()

        return CsvTemplateResponse(
            columns=template_data["columns"],
            required_columns=template_data["required_columns"],
            sample_data=template_data["sample_data"],
            description="顧客組織をインポートするためのCSVテンプレートです。会社名と会社URLは必須項目です。",
        )
    except Exception as e:
        logger.error(
            f"Failed to get CSV template: {str(e)}",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CSVテンプレートの取得に失敗しました",
        ) from e


@router.post(
    "/validate",
    response_model=CsvValidationResponse,
    summary="CSVファイルバリデーション",
    description="アップロードされたCSVファイルをバリデーションします",
)
async def validate_csv_file(
    file: UploadFile = File(..., description="CSVファイル"),
    column_mappings: list[ColumnMappingSchema] = None,
    encoding: str = "utf-8",
    current_user: UserEntity = Depends(get_current_active_user),
    use_case: CsvImportUseCase = Depends(get_csv_import_use_case),
) -> CsvValidationResponse:
    """
    CSVファイルをバリデーション

    Args:
        file: アップロードされたCSVファイル
        column_mappings: カラムマッピングのリスト
        encoding: ファイルエンコーディング
        current_user: 現在のユーザー
        use_case: CSVインポートユースケース

    Returns:
        バリデーション結果

    Raises:
        HTTPException: バリデーションエラーまたはファイル読み込みエラー
    """
    # ファイル内容を読み込み
    file_content = await file.read()

    # セキュリティ検証（拡張子、Content-Type、サイズ、マジックナンバー）
    validate_csv_file_security(file, file_content)

    # カラムマッピングが指定されていない場合、デフォルトマッピングを使用
    if not column_mappings:
        template_data = await use_case.get_csv_template()
        column_mappings = [
            ColumnMappingSchema(
                csv_column_name=col,
                system_field_name=col,
                is_required=col in template_data["required_columns"],
            )
            for col in template_data["columns"]
        ]

    try:
        # バリデーション実行
        result = await use_case.validate_csv_file(
            file_content=file_content,
            column_mappings=column_mappings,
            encoding=encoding,
        )

        logger.info(
            f"CSV validation completed: {result.total_rows} rows",
            extra={
                "user_id": current_user.id,
                "is_valid": result.is_valid,
                "total_rows": result.total_rows,
            },
        )

        return result

    except ValueError as e:
        logger.error(
            f"CSV validation failed: {str(e)}",
            extra={"user_id": current_user.id, "filename": file.filename},
        )
        # セキュリティ: 内部エラー詳細を露出しない
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルの形式が正しくありません。テンプレートを確認してください。",
        ) from e
    except Exception as e:
        logger.error(
            f"Unexpected error during CSV validation: {str(e)}",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CSVバリデーション中にエラーが発生しました",
        ) from e


@router.post(
    "/import",
    response_model=ImportResultResponse,
    summary="CSVインポート実行",
    description="バリデーション済みのCSVファイルから顧客組織をインポートします",
    status_code=status.HTTP_201_CREATED,
)
async def execute_csv_import(
    file: UploadFile = File(..., description="CSVファイル"),
    request: ImportExecuteRequest = None,
    current_user: UserEntity = Depends(get_current_active_user),
    use_case: CsvImportUseCase = Depends(get_csv_import_use_case),
) -> ImportResultResponse:
    """
    CSVファイルから顧客組織をインポート

    Args:
        file: アップロードされたCSVファイル
        request: インポート実行リクエスト
        current_user: 現在のユーザー
        use_case: CSVインポートユースケース

    Returns:
        インポート結果

    Raises:
        HTTPException: インポートエラー
    """
    # ファイル内容を読み込み
    file_content = await file.read()

    # セキュリティ検証（拡張子、Content-Type、サイズ、マジックナンバー）
    validate_csv_file_security(file, file_content)

    # リクエストが指定されていない場合、デフォルト値を使用
    if not request:
        template_data = await use_case.get_csv_template()
        column_mappings = [
            ColumnMappingSchema(
                csv_column_name=col,
                system_field_name=col,
                is_required=col in template_data["required_columns"],
            )
            for col in template_data["columns"]
        ]
        encoding = "utf-8"
        skip_validation = False
    else:
        column_mappings = request.column_mappings
        encoding = request.encoding
        skip_validation = request.skip_validation

    try:
        # 現在のユーザーの組織IDを親組織として使用
        parent_organization_id = current_user.organization_id

        # インポート実行
        result = await use_case.execute_import(
            file_content=file_content,
            column_mappings=column_mappings,
            parent_organization_id=parent_organization_id,
            encoding=encoding,
            skip_validation=skip_validation,
        )

        logger.info(
            f"CSV import completed: {result.successful_rows}/{result.total_rows} rows imported",
            extra={
                "user_id": current_user.id,
                "organization_id": parent_organization_id,
                "total_rows": result.total_rows,
                "successful_rows": result.successful_rows,
                "failed_rows": result.failed_rows,
            },
        )

        return result

    except ValueError as e:
        logger.error(
            f"CSV import failed: {str(e)}",
            extra={"user_id": current_user.id, "filename": file.filename},
        )
        # セキュリティ: 内部エラー詳細を露出しない
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルのインポートに失敗しました。データ形式を確認してください。",
        ) from e
    except Exception as e:
        logger.error(
            f"Unexpected error during CSV import: {str(e)}",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CSVインポート中にエラーが発生しました",
        ) from e
