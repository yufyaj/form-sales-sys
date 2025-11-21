"""
CSVインポートAPI

顧客組織のCSVインポート機能を提供するAPIエンドポイント。
- CSVアップロード
- カラムマッピング
- バリデーション
- インポート実行
"""

import logging

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
    # ファイルタイプのバリデーション
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルのみアップロード可能です",
        )

    # ファイルサイズのバリデーション（10MB制限）
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="ファイルサイズが大きすぎます（最大10MB）",
        )

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
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
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
    # ファイルタイプのバリデーション
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルのみアップロード可能です",
        )

    # ファイルサイズのバリデーション（10MB制限）
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="ファイルサイズが大きすぎます（最大10MB）",
        )

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
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
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
