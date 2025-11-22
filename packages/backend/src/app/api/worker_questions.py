"""
ワーカー質問管理APIルーター

ワーカー質問のCRUD操作のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.worker_question import (
    UnreadCountResponse,
    WorkerQuestionAnswerRequest,
    WorkerQuestionCreateRequest,
    WorkerQuestionListResponse,
    WorkerQuestionResponse,
    WorkerQuestionUpdateRequest,
)
from src.application.use_cases.worker_question_use_cases import WorkerQuestionUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.worker_question_repository import (
    WorkerQuestionRepository,
)
from src.infrastructure.persistence.repositories.worker_repository import WorkerRepository

router = APIRouter(prefix="/worker-questions", tags=["worker-questions"])


async def get_worker_question_use_cases(
    session: AsyncSession = Depends(get_db),
) -> WorkerQuestionUseCases:
    """
    ワーカー質問ユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        WorkerQuestionUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    question_repo = WorkerQuestionRepository(session)
    worker_repo = WorkerRepository(session)

    # ユースケースをインスタンス化
    use_cases = WorkerQuestionUseCases(
        worker_question_repository=question_repo,
        worker_repository=worker_repo,
    )

    return use_cases


@router.post(
    "",
    response_model=WorkerQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ワーカー質問作成",
    description="新規ワーカー質問を作成します。ワーカー自身が質問を投稿します。認証が必要です。",
)
async def create_question(
    request: WorkerQuestionCreateRequest,
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionResponse:
    """
    新規ワーカー質問を作成

    - **title**: 質問タイトル（必須、最大500文字）
    - **content**: 質問内容（必須）
    - **client_organization_id**: 関連する顧客組織ID（オプション）
    - **priority**: 質問優先度（オプション、デフォルト: medium）
    - **tags**: タグ（オプション、JSON配列形式）

    Note:
        ワーカーのuser_idは認証情報から自動的に取得されます。
        ワーカーとして登録されているユーザーのみが質問を投稿できます。
    """
    # TODO: current_userからworker_idを取得する実装が必要
    # 現時点では、ワーカーテーブルからuser_idで検索する必要がある
    # 仮にworker_idを1として実装（実際にはワーカーリポジトリで検索）
    worker_id = 1  # TODO: 実装が必要

    question = await use_cases.create_question(
        request, worker_id, current_user.organization_id
    )
    return WorkerQuestionResponse.model_validate(question)


@router.get(
    "/{question_id}",
    response_model=WorkerQuestionResponse,
    summary="ワーカー質問取得",
    description="指定されたIDのワーカー質問を取得します。認証が必要です。",
)
async def get_question(
    question_id: int,
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionResponse:
    """
    ワーカー質問を取得

    - **question_id**: 質問ID
    """
    question = await use_cases.get_question(question_id, current_user.organization_id)
    return WorkerQuestionResponse.model_validate(question)


@router.get(
    "",
    response_model=WorkerQuestionListResponse,
    summary="ワーカー質問一覧取得",
    description="組織に所属するワーカー質問一覧を取得します。認証が必要です。",
)
async def list_questions(
    status: str | None = Query(None, description="フィルタ用ステータス"),
    worker_id: int | None = Query(None, description="フィルタ用ワーカーID"),
    client_organization_id: int | None = Query(None, description="フィルタ用顧客組織ID"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=500, description="取得する最大件数"),
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionListResponse:
    """
    組織のワーカー質問一覧を取得

    - **status**: フィルタ用ステータス（オプション）
    - **worker_id**: フィルタ用ワーカーID（オプション）
    - **client_organization_id**: フィルタ用顧客組織ID（オプション）
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    question_list, total = await use_cases.list_questions_by_organization(
        current_user.organization_id,
        status,
        worker_id,
        client_organization_id,
        skip,
        limit,
    )
    return WorkerQuestionListResponse(
        questions=[WorkerQuestionResponse.model_validate(q) for q in question_list],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/workers/{worker_id}",
    response_model=WorkerQuestionListResponse,
    summary="特定ワーカーの質問一覧取得",
    description="特定のワーカーの質問一覧を取得します。認証が必要です。",
)
async def list_questions_by_worker(
    worker_id: int,
    status: str | None = Query(None, description="フィルタ用ステータス"),
    skip: int = Query(0, ge=0, description="スキップする件数"),
    limit: int = Query(100, ge=1, le=500, description="取得する最大件数"),
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionListResponse:
    """
    特定のワーカーの質問一覧を取得

    - **worker_id**: ワーカーID
    - **status**: フィルタ用ステータス（オプション）
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    question_list, total = await use_cases.list_questions_by_worker(
        worker_id,
        current_user.organization_id,
        status,
        skip,
        limit,
    )
    return WorkerQuestionListResponse(
        questions=[WorkerQuestionResponse.model_validate(q) for q in question_list],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{question_id}",
    response_model=WorkerQuestionResponse,
    summary="ワーカー質問更新",
    description="ワーカー質問情報を更新します。認証が必要です。",
)
async def update_question(
    question_id: int,
    request: WorkerQuestionUpdateRequest,
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionResponse:
    """
    ワーカー質問情報を更新

    - **question_id**: 質問ID
    - **request**: 更新内容（部分更新可能）
    """
    question = await use_cases.update_question(
        question_id, current_user.organization_id, request
    )
    return WorkerQuestionResponse.model_validate(question)


@router.post(
    "/{question_id}/answer",
    response_model=WorkerQuestionResponse,
    summary="ワーカー質問に回答",
    description="ワーカー質問に回答を追加します。営業支援会社のスタッフが実行します。認証が必要です。",
)
async def add_answer(
    question_id: int,
    request: WorkerQuestionAnswerRequest,
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> WorkerQuestionResponse:
    """
    ワーカー質問に回答を追加

    - **question_id**: 質問ID
    - **answer**: 回答内容

    Note:
        回答を追加すると、質問のステータスが自動的に"answered"に変更されます。
    """
    question = await use_cases.add_answer(
        question_id,
        current_user.organization_id,
        request,
        current_user.id,
    )
    return WorkerQuestionResponse.model_validate(question)


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ワーカー質問削除",
    description="ワーカー質問を論理削除します。認証が必要です。",
)
async def delete_question(
    question_id: int,
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    ワーカー質問を論理削除

    - **question_id**: 質問ID
    """
    await use_cases.delete_question(question_id, current_user.organization_id)


@router.get(
    "/stats/unread-count",
    response_model=UnreadCountResponse,
    summary="未読質問数取得",
    description="未読質問数（pendingステータスの質問数）を取得します。認証が必要です。",
)
async def get_unread_count(
    use_cases: WorkerQuestionUseCases = Depends(get_worker_question_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> UnreadCountResponse:
    """
    未読質問数を取得

    営業支援会社のスタッフが、自社のワーカーからの未読質問数を取得します。

    Note:
        未読質問とは、statusが"pending"の質問を指します。
        この値を使ってフロントエンドで通知バッジなどを表示できます。
    """
    unread_count = await use_cases.get_unread_count(current_user.organization_id)
    return UnreadCountResponse(unread_count=unread_count)
