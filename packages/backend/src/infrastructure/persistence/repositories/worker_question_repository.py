"""
ワーカー質問リポジトリの実装

IWorkerQuestionRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.worker_question_entity import WorkerQuestionEntity
from src.domain.exceptions import WorkerQuestionNotFoundError
from src.domain.interfaces.worker_question_repository import IWorkerQuestionRepository
from src.infrastructure.persistence.models.worker_question import (
    QuestionPriority,
    QuestionStatus,
    WorkerQuestion,
)

# セキュリティログ用のロガー
logger = logging.getLogger(__name__)


class WorkerQuestionRepository(IWorkerQuestionRepository):
    """
    ワーカー質問リポジトリの実装

    SQLAlchemyを使用してワーカー質問の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        worker_id: int,
        organization_id: int,
        title: str,
        content: str,
        client_organization_id: int | None = None,
        status: str = "pending",
        priority: str = "medium",
        tags: str | None = None,
    ) -> WorkerQuestionEntity:
        """ワーカー質問を作成"""
        question = WorkerQuestion(
            worker_id=worker_id,
            organization_id=organization_id,
            client_organization_id=client_organization_id,
            title=title,
            content=content,
            status=QuestionStatus(status),
            priority=QuestionPriority(priority),
            tags=tags,
        )

        self._session.add(question)
        await self._session.flush()
        await self._session.refresh(question)

        logger.info(
            "Worker question created successfully",
            extra={
                "event_type": "worker_question_created",
                "question_id": question.id,
                "organization_id": organization_id,  # 監査ログとして必要
                "status": status,
                "priority": priority,
                # worker_idは機密情報のため、監査要件がない限り出力しない
            },
        )

        return self._to_entity(question)

    async def find_by_id(
        self,
        question_id: int,
        requesting_organization_id: int,
    ) -> WorkerQuestionEntity | None:
        """IDでワーカー質問を検索（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(WorkerQuestion).where(
            WorkerQuestion.id == question_id,
            WorkerQuestion.organization_id == requesting_organization_id,
            WorkerQuestion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        question = result.scalar_one_or_none()

        # IDOR攻撃検出ログ
        if question is None:
            check_stmt = select(WorkerQuestion).where(
                WorkerQuestion.id == question_id,
                WorkerQuestion.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_question = check_result.scalar_one_or_none()

            if actual_question is not None:
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant access attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_question_access",
                        "question_id": question_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_question.organization_id,
                    },
                )

        return self._to_entity(question) if question else None

    async def list_by_organization(
        self,
        organization_id: int,
        status: str | None = None,
        worker_id: int | None = None,
        client_organization_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkerQuestionEntity]:
        """営業支援会社に属するワーカー質問の一覧を取得"""
        conditions = [WorkerQuestion.organization_id == organization_id]

        if status is not None:
            conditions.append(WorkerQuestion.status == QuestionStatus(status))
        if worker_id is not None:
            conditions.append(WorkerQuestion.worker_id == worker_id)
        if client_organization_id is not None:
            conditions.append(WorkerQuestion.client_organization_id == client_organization_id)
        if not include_deleted:
            conditions.append(WorkerQuestion.deleted_at.is_(None))

        stmt = (
            select(WorkerQuestion)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(WorkerQuestion.created_at.desc())
        )

        result = await self._session.execute(stmt)
        question_list = result.scalars().all()

        return [self._to_entity(q) for q in question_list]

    async def list_by_worker(
        self,
        worker_id: int,
        organization_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkerQuestionEntity]:
        """特定のワーカーの質問一覧を取得（マルチテナント対応）"""
        conditions = [
            WorkerQuestion.worker_id == worker_id,
            WorkerQuestion.organization_id == organization_id,
        ]

        if status is not None:
            conditions.append(WorkerQuestion.status == QuestionStatus(status))
        if not include_deleted:
            conditions.append(WorkerQuestion.deleted_at.is_(None))

        stmt = (
            select(WorkerQuestion)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(WorkerQuestion.created_at.desc())
        )

        result = await self._session.execute(stmt)
        question_list = result.scalars().all()

        return [self._to_entity(q) for q in question_list]

    async def count_by_organization(
        self,
        organization_id: int,
        status: str | None = None,
        worker_id: int | None = None,
        client_organization_id: int | None = None,
        include_deleted: bool = False,
    ) -> int:
        """営業支援会社に属するワーカー質問の総件数を取得"""
        conditions = [WorkerQuestion.organization_id == organization_id]

        if status is not None:
            conditions.append(WorkerQuestion.status == QuestionStatus(status))
        if worker_id is not None:
            conditions.append(WorkerQuestion.worker_id == worker_id)
        if client_organization_id is not None:
            conditions.append(WorkerQuestion.client_organization_id == client_organization_id)
        if not include_deleted:
            conditions.append(WorkerQuestion.deleted_at.is_(None))

        stmt = select(func.count()).select_from(WorkerQuestion).where(and_(*conditions))

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def count_by_worker(
        self,
        worker_id: int,
        organization_id: int,
        status: str | None = None,
        include_deleted: bool = False,
    ) -> int:
        """特定のワーカーの質問総件数を取得（マルチテナント対応）"""
        conditions = [
            WorkerQuestion.worker_id == worker_id,
            WorkerQuestion.organization_id == organization_id,
        ]

        if status is not None:
            conditions.append(WorkerQuestion.status == QuestionStatus(status))
        if not include_deleted:
            conditions.append(WorkerQuestion.deleted_at.is_(None))

        stmt = select(func.count()).select_from(WorkerQuestion).where(and_(*conditions))

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def update(
        self,
        question: WorkerQuestionEntity,
        requesting_organization_id: int,
    ) -> WorkerQuestionEntity:
        """ワーカー質問情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(WorkerQuestion).where(
            WorkerQuestion.id == question.id,
            WorkerQuestion.organization_id == requesting_organization_id,
            WorkerQuestion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_question = result.scalar_one_or_none()

        if db_question is None:
            check_stmt = select(WorkerQuestion).where(
                WorkerQuestion.id == question.id,
                WorkerQuestion.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_question = check_result.scalar_one_or_none()

            if actual_question is not None:
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant update attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_question_update",
                        "question_id": question.id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_question.organization_id,
                    },
                )

            raise WorkerQuestionNotFoundError(question.id)

        # エンティティの値でモデルを更新
        db_question.title = question.title
        db_question.content = question.content
        db_question.status = QuestionStatus(question.status)
        db_question.priority = QuestionPriority(question.priority)
        db_question.answer = question.answer
        db_question.answered_by_user_id = question.answered_by_user_id
        db_question.answered_at = question.answered_at
        db_question.tags = question.tags
        db_question.internal_notes = question.internal_notes

        await self._session.flush()
        await self._session.refresh(db_question)

        logger.info(
            "Worker question updated successfully",
            extra={
                "event_type": "worker_question_updated",
                "question_id": question.id,
                "organization_id": requesting_organization_id,
            },
        )

        return self._to_entity(db_question)

    async def add_answer(
        self,
        question_id: int,
        requesting_organization_id: int,
        answer: str,
        answered_by_user_id: int,
    ) -> WorkerQuestionEntity:
        """ワーカー質問に回答を追加（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(WorkerQuestion).where(
            WorkerQuestion.id == question_id,
            WorkerQuestion.organization_id == requesting_organization_id,
            WorkerQuestion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        question = result.scalar_one_or_none()

        if question is None:
            check_stmt = select(WorkerQuestion).where(
                WorkerQuestion.id == question_id,
                WorkerQuestion.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_question = check_result.scalar_one_or_none()

            if actual_question is not None:
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant answer attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_question_answer",
                        "question_id": question_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_question.organization_id,
                    },
                )

            raise WorkerQuestionNotFoundError(question_id)

        # 回答を追加し、ステータスを更新
        question.answer = answer
        question.answered_by_user_id = answered_by_user_id
        question.answered_at = datetime.now(timezone.utc)
        question.status = QuestionStatus.ANSWERED

        await self._session.flush()
        await self._session.refresh(question)

        logger.info(
            "Answer added to worker question successfully",
            extra={
                "event_type": "worker_question_answered",
                "question_id": question_id,
                "answered_by_user_id": answered_by_user_id,
                "organization_id": requesting_organization_id,
            },
        )

        return self._to_entity(question)

    async def soft_delete(
        self,
        question_id: int,
        requesting_organization_id: int,
    ) -> None:
        """ワーカー質問を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        stmt = select(WorkerQuestion).where(
            WorkerQuestion.id == question_id,
            WorkerQuestion.organization_id == requesting_organization_id,
            WorkerQuestion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        question = result.scalar_one_or_none()

        if question is None:
            check_stmt = select(WorkerQuestion).where(
                WorkerQuestion.id == question_id,
                WorkerQuestion.deleted_at.is_(None),
            )
            check_result = await self._session.execute(check_stmt)
            actual_question = check_result.scalar_one_or_none()

            if actual_question is not None:
                logger.warning(
                    "Potential IDOR attack detected: cross-tenant delete attempt",
                    extra={
                        "event_type": "idor_attack_detected",
                        "attack_type": "worker_question_delete",
                        "question_id": question_id,
                        "requesting_organization_id": requesting_organization_id,
                        "actual_organization_id": actual_question.organization_id,
                    },
                )

            raise WorkerQuestionNotFoundError(question_id)

        question.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        logger.info(
            "Worker question soft deleted successfully",
            extra={
                "event_type": "worker_question_deleted",
                "question_id": question_id,
                "organization_id": requesting_organization_id,
                # worker_idは機密情報のため、監査要件がない限り出力しない
            },
        )

    def _to_entity(self, question: WorkerQuestion) -> WorkerQuestionEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return WorkerQuestionEntity(
            id=question.id,
            worker_id=question.worker_id,
            organization_id=question.organization_id,
            client_organization_id=question.client_organization_id,
            title=question.title,
            content=question.content,
            status=question.status.value,
            priority=question.priority.value,
            answer=question.answer,
            answered_by_user_id=question.answered_by_user_id,
            answered_at=question.answered_at,
            tags=question.tags,
            internal_notes=question.internal_notes,
            created_at=question.created_at,
            updated_at=question.updated_at,
            deleted_at=question.deleted_at,
        )
