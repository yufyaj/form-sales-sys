"""
作業記録APIルーター

作業記録のCRUD操作のエンドポイントを提供します
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_current_worker_id, get_db
from src.application.schemas.work_record import (
    WorkRecordCreateRequest,
    WorkRecordListResponse,
    WorkRecordResponse,
    WorkRecordUpdateRequest,
)
from src.application.use_cases.work_record_use_cases import WorkRecordUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.models.work_record import WorkRecordStatus
from src.infrastructure.persistence.repositories.work_record_repository import WorkRecordRepository
from src.infrastructure.persistence.repositories.no_send_setting_repository import NoSendSettingRepository

router = APIRouter(prefix="/work-records", tags=["work-records"])


async def get_work_record_use_cases(
    session: AsyncSession = Depends(get_db),
) -> WorkRecordUseCases:
    """
    作業記録ユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        WorkRecordUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    work_record_repo = WorkRecordRepository(session)
    no_send_setting_repo = NoSendSettingRepository(session)

    # ユースケースをインスタンス化
    use_cases = WorkRecordUseCases(
        work_record_repository=work_record_repo,
        no_send_setting_repository=no_send_setting_repo,
    )

    return use_cases


@router.post(
    "",
    response_model=WorkRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="作業記録作成",
    description="新規作業記録を作成します。認証が必要です。送信禁止設定のチェックも行います。",
)
async def create_work_record(
    request: WorkRecordCreateRequest,
    list_id: int = Query(..., description="リストID（送信制御チェック用）"),
    use_cases: WorkRecordUseCases = Depends(get_work_record_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkRecordResponse:
    """
    新規作業記録を作成

    - **assignment_id**: リスト項目割り当てID
    - **worker_id**: ワーカーID
    - **status**: 送信済み or 送信不可
    - **started_at**: 作業開始日時
    - **completed_at**: 作業完了日時
    - **form_submission_result**: 送信結果の詳細（JSON）
    - **cannot_send_reason_id**: 送信不可理由ID（送信不可の場合のみ）
    - **notes**: メモ・備考

    送信済み（SENT）の場合は送信禁止設定をチェックし、違反している場合はエラーを返します。
    """
    work_record = await use_cases.create_work_record(request, list_id)
    return WorkRecordResponse.model_validate(work_record)


@router.get(
    "/{record_id}",
    response_model=WorkRecordResponse,
    summary="作業記録取得",
    description="指定されたIDの作業記録を取得します。認証が必要です。",
)
async def get_work_record(
    record_id: int,
    worker_id: int = Depends(get_current_worker_id),
    use_cases: WorkRecordUseCases = Depends(get_work_record_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkRecordResponse:
    """
    作業記録を取得

    - **record_id**: 作業記録ID

    IDOR対策として、get_current_worker_idでログイン中のユーザーのworker_idのみを取得し、
    requesting_worker_idとrequesting_organization_idでアクセス権限をチェックします。
    """
    work_record = await use_cases.get_work_record(
        record_id=record_id,
        requesting_worker_id=worker_id,
        requesting_organization_id=current_user.organization_id,
    )
    return WorkRecordResponse.model_validate(work_record)


@router.get(
    "",
    response_model=WorkRecordListResponse,
    summary="作業記録一覧取得",
    description="ログイン中のワーカーの作業記録一覧を取得します。認証が必要です。",
)
async def list_work_records(
    worker_id: int = Depends(get_current_worker_id),
    status: WorkRecordStatus | None = Query(None, description="フィルタ用ステータス"),
    start_date: datetime | None = Query(None, description="検索開始日時"),
    end_date: datetime | None = Query(None, description="検索終了日時"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=500, description="取得する最大件数"),
    use_cases: WorkRecordUseCases = Depends(get_work_record_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkRecordListResponse:
    """
    ログイン中のワーカーの作業記録一覧を取得（IDOR対策）

    IDOR脆弱性対策として、クエリパラメータでworker_idを受け取らず、
    get_current_worker_idでログイン中のユーザーのworker_idのみを使用します。
    これにより、他のワーカーの作業記録を閲覧することを防止します。

    - **status**: フィルタ用ステータス（オプション）
    - **start_date**: 検索開始日時（オプション）
    - **end_date**: 検索終了日時（オプション）
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    records, total = await use_cases.list_work_records_by_worker(
        worker_id=worker_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return WorkRecordListResponse(
        records=[WorkRecordResponse.model_validate(r) for r in records],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{record_id}",
    response_model=WorkRecordResponse,
    summary="作業記録更新",
    description="作業記録を更新します。認証が必要です。",
)
async def update_work_record(
    record_id: int,
    request: WorkRecordUpdateRequest,
    worker_id: int = Depends(get_current_worker_id),
    use_cases: WorkRecordUseCases = Depends(get_work_record_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkRecordResponse:
    """
    作業記録を更新

    - **record_id**: 作業記録ID
    - **request**: 更新内容（部分更新可能）

    IDOR対策として、get_current_worker_idでログイン中のユーザーのworker_idのみを取得し、
    requesting_worker_idとrequesting_organization_idでアクセス権限をチェックします。
    """
    work_record = await use_cases.update_work_record(
        record_id=record_id,
        request=request,
        requesting_worker_id=worker_id,
        requesting_organization_id=current_user.organization_id,
    )
    return WorkRecordResponse.model_validate(work_record)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="作業記録削除",
    description="作業記録を論理削除します。認証が必要です。",
)
async def delete_work_record(
    record_id: int,
    worker_id: int = Depends(get_current_worker_id),
    use_cases: WorkRecordUseCases = Depends(get_work_record_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    作業記録を論理削除

    - **record_id**: 作業記録ID

    IDOR対策として、get_current_worker_idでログイン中のユーザーのworker_idのみを取得し、
    requesting_worker_idとrequesting_organization_idでアクセス権限をチェックします。
    """
    await use_cases.delete_work_record(
        record_id=record_id,
        requesting_worker_id=worker_id,
        requesting_organization_id=current_user.organization_id,
    )
