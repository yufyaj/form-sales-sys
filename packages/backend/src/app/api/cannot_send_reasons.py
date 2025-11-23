"""
送信不可理由管理APIルーター

送信不可理由マスタデータのCRUD操作エンドポイントを提供します。
営業支援会社がカスタマイズ可能なマスタデータです。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, RoleChecker
from src.app.core.database import get_db
from src.application.schemas.cannot_send_reason import (
    CannotSendReasonCreateRequest,
    CannotSendReasonListResponse,
    CannotSendReasonResponse,
    CannotSendReasonUpdateRequest,
)
from src.application.use_cases.cannot_send_reason_use_cases import (
    CannotSendReasonUseCases,
)
from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.cannot_send_reason_repository import (
    ICannotSendReasonRepository,
)
from src.infrastructure.persistence.repositories.cannot_send_reason_repository import (
    CannotSendReasonRepository,
)

router = APIRouter(prefix="/cannot-send-reasons", tags=["cannot-send-reasons"])

# レート制限の初期化
limiter = Limiter(key_func=get_remote_address)


async def get_cannot_send_reason_use_cases(
    session: AsyncSession = Depends(get_db),
) -> CannotSendReasonUseCases:
    """
    送信不可理由ユースケースの依存性注入

    Args:
        session: データベースセッション

    Returns:
        CannotSendReasonUseCases: 送信不可理由ユースケースインスタンス
    """
    repo: ICannotSendReasonRepository = CannotSendReasonRepository(session)
    return CannotSendReasonUseCases(cannot_send_reason_repository=repo)


@router.post(
    "",
    response_model=CannotSendReasonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="送信不可理由を作成",
    description="新しい送信不可理由を作成します。管理者権限が必要です。",
)
@limiter.limit("10/minute")
async def create_reason(
    http_request: Request,
    reason_request: CannotSendReasonCreateRequest,
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
    use_cases: CannotSendReasonUseCases = Depends(get_cannot_send_reason_use_cases),
) -> CannotSendReasonResponse:
    """
    送信不可理由を作成

    - **reason_code**: 理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）
    - **reason_name**: 理由名
    - **description**: 詳細説明（任意）
    - **is_active**: 有効/無効フラグ（デフォルト: true）
    """
    reason = await use_cases.create_reason(request=reason_request)
    return _to_response(reason)


@router.get(
    "/{reason_id}",
    response_model=CannotSendReasonResponse,
    summary="送信不可理由を取得",
    description="IDで送信不可理由を取得します。認証が必要です。",
)
async def get_reason(
    reason_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: CannotSendReasonUseCases = Depends(get_cannot_send_reason_use_cases),
) -> CannotSendReasonResponse:
    """
    送信不可理由を取得

    - **reason_id**: 送信不可理由ID
    """
    reason = await use_cases.get_reason(reason_id=reason_id)
    return _to_response(reason)


@router.get(
    "",
    response_model=CannotSendReasonListResponse,
    summary="送信不可理由一覧を取得",
    description="送信不可理由の一覧を取得します。認証が必要です。",
)
async def list_reasons(
    is_active_only: Annotated[
        bool,
        Query(description="有効な理由のみを取得するか"),
    ] = True,
    skip: Annotated[int, Query(ge=0, description="スキップする件数")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="取得する最大件数")] = 100,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: CannotSendReasonUseCases = Depends(get_cannot_send_reason_use_cases),
) -> CannotSendReasonListResponse:
    """
    送信不可理由の一覧を取得

    - **is_active_only**: 有効な理由のみを取得するか（デフォルト: true）
    - **skip**: スキップする件数（ページネーション用、デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100、最大: 1000）
    """
    reasons, total = await use_cases.list_reasons(
        is_active_only=is_active_only,
        skip=skip,
        limit=limit,
    )

    return CannotSendReasonListResponse(
        reasons=[_to_response(reason) for reason in reasons],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{reason_id}",
    response_model=CannotSendReasonResponse,
    summary="送信不可理由を更新",
    description="送信不可理由を部分的に更新します。管理者権限が必要です。",
)
@limiter.limit("20/minute")
async def update_reason(
    http_request: Request,
    reason_id: int,
    reason_request: CannotSendReasonUpdateRequest,
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
    use_cases: CannotSendReasonUseCases = Depends(get_cannot_send_reason_use_cases),
) -> CannotSendReasonResponse:
    """
    送信不可理由を更新

    - **reason_id**: 送信不可理由ID
    - **reason_code**: 理由コード（任意）
    - **reason_name**: 理由名（任意）
    - **description**: 詳細説明（任意）
    - **is_active**: 有効/無効フラグ（任意）
    """
    reason = await use_cases.update_reason(reason_id=reason_id, request=reason_request)
    return _to_response(reason)


@router.delete(
    "/{reason_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="送信不可理由を削除",
    description="送信不可理由を論理削除します。管理者権限が必要です。",
)
@limiter.limit("10/minute")
async def delete_reason(
    http_request: Request,
    reason_id: int,
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
    use_cases: CannotSendReasonUseCases = Depends(get_cannot_send_reason_use_cases),
) -> None:
    """
    送信不可理由を論理削除

    - **reason_id**: 送信不可理由ID
    """
    await use_cases.delete_reason(reason_id=reason_id)


def _to_response(
    reason: CannotSendReasonEntity,
) -> CannotSendReasonResponse:
    """
    CannotSendReasonEntityをCannotSendReasonResponseに変換

    Args:
        reason: 送信不可理由エンティティ

    Returns:
        CannotSendReasonResponse: 送信不可理由レスポンス
    """
    return CannotSendReasonResponse(
        id=reason.id,
        reason_code=reason.reason_code,
        reason_name=reason.reason_name,
        description=reason.description,
        is_active=reason.is_active,
        created_at=reason.created_at,
        updated_at=reason.updated_at,
        deleted_at=reason.deleted_at,
    )
