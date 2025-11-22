"""
ワーカー質問管理のユースケース

ワーカー質問のCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.worker_question import (
    WorkerQuestionAnswerRequest,
    WorkerQuestionCreateRequest,
    WorkerQuestionUpdateRequest,
)
from src.domain.entities.worker_question_entity import WorkerQuestionEntity
from src.domain.exceptions import (
    WorkerNotFoundError,
    WorkerQuestionCannotBeAnsweredError,
    WorkerQuestionNotFoundError,
)
from src.domain.interfaces.worker_question_repository import IWorkerQuestionRepository
from src.domain.interfaces.worker_repository import IWorkerRepository


class WorkerQuestionUseCases:
    """ワーカー質問管理のユースケースクラス"""

    def __init__(
        self,
        worker_question_repository: IWorkerQuestionRepository,
        worker_repository: IWorkerRepository,
    ) -> None:
        """
        Args:
            worker_question_repository: ワーカー質問リポジトリ
            worker_repository: ワーカーリポジトリ
        """
        self._question_repo = worker_question_repository
        self._worker_repo = worker_repository

    async def create_question(
        self,
        request: WorkerQuestionCreateRequest,
        worker_id: int,
        organization_id: int,
    ) -> WorkerQuestionEntity:
        """
        新規ワーカー質問を作成

        Args:
            request: ワーカー質問作成リクエスト
            worker_id: ワーカーID（質問者）
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            作成されたワーカー質問エンティティ

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合
        """
        # ワーカーの存在確認（マルチテナント対応）
        worker = await self._worker_repo.find_by_id(worker_id, organization_id)
        if worker is None:
            raise WorkerNotFoundError(worker_id)

        # リポジトリで永続化
        question = await self._question_repo.create(
            worker_id=worker_id,
            organization_id=organization_id,
            title=request.title,
            content=request.content,
            client_organization_id=request.client_organization_id,
            priority=request.priority.value,
            tags=request.tags,
        )
        return question

    async def get_question(
        self,
        question_id: int,
        organization_id: int,
    ) -> WorkerQuestionEntity:
        """
        ワーカー質問を取得

        Args:
            question_id: 質問ID
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            ワーカー質問エンティティ

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合
        """
        question = await self._question_repo.find_by_id(question_id, organization_id)
        if question is None:
            raise WorkerQuestionNotFoundError(question_id)
        return question

    async def list_questions_by_organization(
        self,
        organization_id: int,
        status: str | None = None,
        worker_id: int | None = None,
        client_organization_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[WorkerQuestionEntity], int]:
        """
        組織のワーカー質問一覧を取得

        Args:
            organization_id: 組織ID
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            worker_id: フィルタ用のワーカーID（Noneの場合は全ワーカー）
            client_organization_id: フィルタ用の顧客組織ID（Noneの場合は全顧客）
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (質問リスト, 総件数)のタプル
        """
        question_list = await self._question_repo.list_by_organization(
            organization_id=organization_id,
            status=status,
            worker_id=worker_id,
            client_organization_id=client_organization_id,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        # 総件数を正確に取得（ページネーション対応）
        total = await self._question_repo.count_by_organization(
            organization_id=organization_id,
            status=status,
            worker_id=worker_id,
            client_organization_id=client_organization_id,
            include_deleted=False,
        )
        return question_list, total

    async def list_questions_by_worker(
        self,
        worker_id: int,
        organization_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[WorkerQuestionEntity], int]:
        """
        特定のワーカーの質問一覧を取得

        Args:
            worker_id: ワーカーID
            organization_id: 組織ID（マルチテナント対応）
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (質問リスト, 総件数)のタプル

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合
        """
        # ワーカーの存在確認（マルチテナント対応）
        worker = await self._worker_repo.find_by_id(worker_id, organization_id)
        if worker is None:
            raise WorkerNotFoundError(worker_id)

        question_list = await self._question_repo.list_by_worker(
            worker_id=worker_id,
            organization_id=organization_id,
            status=status,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        # 総件数を正確に取得（ページネーション対応）
        total = await self._question_repo.count_by_worker(
            worker_id=worker_id,
            organization_id=organization_id,
            status=status,
            include_deleted=False,
        )
        return question_list, total

    async def update_question(
        self,
        question_id: int,
        organization_id: int,
        request: WorkerQuestionUpdateRequest,
    ) -> WorkerQuestionEntity:
        """
        ワーカー質問情報を更新

        Args:
            question_id: 質問ID
            organization_id: 組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新されたワーカー質問エンティティ

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合
        """
        # 質問を取得
        question = await self._question_repo.find_by_id(question_id, organization_id)
        if question is None:
            raise WorkerQuestionNotFoundError(question_id)

        # フィールドを更新（リクエストに含まれるフィールドのみ）
        if request.title is not None:
            question.title = request.title

        if request.content is not None:
            question.content = request.content

        if request.status is not None:
            question.status = request.status.value

        if request.priority is not None:
            question.priority = request.priority.value

        if request.tags is not None:
            question.tags = request.tags

        if request.internal_notes is not None:
            question.internal_notes = request.internal_notes

        # リポジトリで永続化
        updated_question = await self._question_repo.update(question, organization_id)
        return updated_question

    async def add_answer(
        self,
        question_id: int,
        organization_id: int,
        request: WorkerQuestionAnswerRequest,
        answered_by_user_id: int,
    ) -> WorkerQuestionEntity:
        """
        ワーカー質問に回答を追加

        Args:
            question_id: 質問ID
            organization_id: 組織ID（マルチテナント対応）
            request: 回答リクエスト
            answered_by_user_id: 回答者のユーザーID

        Returns:
            更新されたワーカー質問エンティティ

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合
            WorkerQuestionCannotBeAnsweredError: 質問が回答不可能な状態の場合
        """
        # 質問を取得
        question = await self._question_repo.find_by_id(question_id, organization_id)
        if question is None:
            raise WorkerQuestionNotFoundError(question_id)

        # ビジネスルール: 回答可能な状態かチェック
        if not question.can_be_answered():
            raise WorkerQuestionCannotBeAnsweredError(
                question_id,
                reason=f"Question status is {question.status}",
            )

        # リポジトリで回答を追加
        updated_question = await self._question_repo.add_answer(
            question_id=question_id,
            requesting_organization_id=organization_id,
            answer=request.answer,
            answered_by_user_id=answered_by_user_id,
        )
        return updated_question

    async def delete_question(
        self,
        question_id: int,
        organization_id: int,
    ) -> None:
        """
        ワーカー質問を論理削除

        Args:
            question_id: 質問ID
            organization_id: 組織ID（マルチテナント対応）

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合
        """
        await self._question_repo.soft_delete(question_id, organization_id)

    async def get_unread_count(
        self,
        organization_id: int,
    ) -> int:
        """
        未読質問数を取得

        Args:
            organization_id: 組織ID

        Returns:
            未読質問数（pendingステータスの質問数）
        """
        count = await self._question_repo.count_by_organization(
            organization_id=organization_id,
            status="pending",
            include_deleted=False,
        )
        return count
