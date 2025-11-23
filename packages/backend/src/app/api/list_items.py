"""
リスト項目管理APIルーター

リスト項目の編集・ステータス変更のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.list_item import (
    ListItemResponse,
    ListItemStatusUpdateRequest,
    ListItemUpdateRequest,
)
from src.application.use_cases.list_item_use_cases import ListItemUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.list_item_repository import (
    ListItemRepository,
)

router = APIRouter(tags=["list-items"])


async def get_list_item_use_cases(
    session: AsyncSession = Depends(get_db),
) -> ListItemUseCases:
    """
    リスト項目ユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        ListItemUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    list_item_repo = ListItemRepository(session)

    # ユースケースをインスタンス化
    use_cases = ListItemUseCases(list_item_repository=list_item_repo)

    return use_cases


@router.patch(
    "/list-items/{list_item_id}",
    response_model=ListItemResponse,
    status_code=status.HTTP_200_OK,
    summary="リスト項目の更新（会社名以外）",
    description="""
    リスト項目の情報を更新します（会社名以外のフィールド）。

    **セキュリティ要件:**
    - JWT認証が必須です
    - リクエスト元の組織に所属するリスト項目のみ更新可能です（IDOR対策）
    - 論理削除されたリスト項目は更新できません

    **更新可能フィールド:**
    - ステータス（status）: pending, contacted, negotiating, closed_won, closed_lost, on_hold

    **更新不可フィールド:**
    - 会社名（title）: 企業の一意性を保証する重要なフィールドのため変更不可

    **処理内容:**
    - リクエストで指定されたフィールドのみを更新します（パッチ更新）
    - 指定されなかったフィールドは変更されません
    - データベースのupdated_atタイムスタンプは自動更新されます

    **エラー:**
    - 400: リスト項目が見つからない、または他組織のリソース
    - 401: 認証が必要
    - 422: バリデーションエラー（無効なステータス値など）
    """,
)
async def update_list_item(
    list_item_id: int,
    request: ListItemUpdateRequest,
    use_cases: ListItemUseCases = Depends(get_list_item_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> ListItemResponse:
    """
    リスト項目の更新（会社名以外）

    - **list_item_id**: リスト項目ID
    - **status**: ステータス（オプション）

    **レスポンス:**
    - **id**: リスト項目ID
    - **list_id**: リストID
    - **title**: 企業名などのタイトル
    - **status**: ステータス
    - **created_at**: 作成日時
    - **updated_at**: 更新日時
    - **deleted_at**: 削除日時（論理削除）

    **処理の流れ:**
    1. リスト項目の存在確認（マルチテナント分離）
    2. 指定されたフィールドを更新
    3. データベースに保存
    4. 更新されたリスト項目を返却
    """
    updated_list_item = await use_cases.update_list_item(
        list_item_id=list_item_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )

    return ListItemResponse.model_validate(updated_list_item)


@router.patch(
    "/list-items/{list_item_id}/status",
    response_model=ListItemResponse,
    status_code=status.HTTP_200_OK,
    summary="リスト項目のステータス変更",
    description="""
    リスト項目のステータスのみを変更します。

    **セキュリティ要件:**
    - JWT認証が必須です
    - リクエスト元の組織に所属するリスト項目のみ更新可能です（IDOR対策）
    - 論理削除されたリスト項目は更新できません

    **ステータス値:**
    - pending: 未対応
    - contacted: 連絡済み
    - negotiating: 商談中
    - closed_won: 受注
    - closed_lost: 失注
    - on_hold: 保留

    **処理内容:**
    - ステータスフィールドのみを更新します
    - データベースのupdated_atタイムスタンプは自動更新されます

    **エラー:**
    - 400: リスト項目が見つからない、または他組織のリソース
    - 401: 認証が必要
    - 422: バリデーションエラー（無効なステータス値など）
    """,
)
async def update_list_item_status(
    list_item_id: int,
    request: ListItemStatusUpdateRequest,
    use_cases: ListItemUseCases = Depends(get_list_item_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> ListItemResponse:
    """
    リスト項目のステータス変更

    - **list_item_id**: リスト項目ID
    - **status**: 新しいステータス（必須）

    **レスポンス:**
    - **id**: リスト項目ID
    - **list_id**: リストID
    - **title**: 企業名などのタイトル
    - **status**: 更新されたステータス
    - **created_at**: 作成日時
    - **updated_at**: 更新日時
    - **deleted_at**: 削除日時（論理削除）

    **処理の流れ:**
    1. リスト項目の存在確認（マルチテナント分離）
    2. ステータスを更新
    3. データベースに保存
    4. 更新されたリスト項目を返却
    """
    updated_list_item = await use_cases.update_list_item_status(
        list_item_id=list_item_id,
        requesting_organization_id=current_user.organization_id,
        request=request,
    )

    return ListItemResponse.model_validate(updated_list_item)
