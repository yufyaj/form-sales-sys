"""
リスト項目割り当てリポジトリの実装

IListItemAssignmentRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。

Note:
    トランザクション管理はこのリポジトリの責任範囲外です。
    呼び出し側（ユースケース層）でトランザクションの開始・コミット・ロールバックを行ってください。
    このリポジトリでは flush() を使用しますが、commit() は呼び出し側に委ねます。
"""
import logging

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from src.domain.entities.list_item_assignment_entity import ListItemAssignmentEntity
from src.domain.exceptions import (
    DuplicateAssignmentError,
    ListItemAssignmentNotFoundError,
    ListItemNotFoundError,
    WorkerNotFoundError,
)
from src.domain.interfaces.list_item_assignment_repository import (
    IListItemAssignmentRepository,
)
from src.infrastructure.persistence.models.list import List
from src.infrastructure.persistence.models.list_item import ListItem
from src.infrastructure.persistence.models.list_item_assignment import ListItemAssignment
from src.infrastructure.persistence.models.worker import Worker


class ListItemAssignmentRepository(IListItemAssignmentRepository):
    """
    リスト項目割り当てリポジトリの実装

    SQLAlchemyを使用してリスト項目とワーカーの割り当て関係の永続化を行います。
    重複割り当ては、データベースの複合ユニーク制約（uq_list_item_worker）で防止されます。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def assign_worker_to_list_item(
        self,
        list_item_id: int,
        worker_id: int,
        requesting_organization_id: int,
    ) -> ListItemAssignmentEntity:
        """
        リスト項目にワーカーを割り当て

        重複割り当てはデータベースの複合ユニーク制約で防止されます。
        """
        # マルチテナント対応: リスト項目の所属組織を検証
        # list_item -> list -> organization を経由してテナント分離
        list_item_stmt = (
            select(ListItem)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItem.id == list_item_id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),
            )
        )
        list_item_result = await self._session.execute(list_item_stmt)
        list_item = list_item_result.scalar_one_or_none()

        if list_item is None:
            raise ListItemNotFoundError(list_item_id)

        # マルチテナント対応: ワーカーの所属組織を検証
        worker_stmt = select(Worker).where(
            Worker.id == worker_id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        worker_result = await self._session.execute(worker_stmt)
        worker = worker_result.scalar_one_or_none()

        if worker is None:
            raise WorkerNotFoundError(worker_id)

        # 割り当てを作成
        assignment = ListItemAssignment(
            list_item_id=list_item_id,
            worker_id=worker_id,
        )

        self._session.add(assignment)

        try:
            await self._session.flush()
            await self._session.refresh(assignment)
        except IntegrityError as e:
            # 複合ユニーク制約違反（uq_list_item_worker）の場合
            # データベースエンジンによるエラーメッセージの違いに対応
            error_msg = str(e.orig).lower()
            if "uq_list_item_worker" in error_msg or "unique constraint" in error_msg:
                raise DuplicateAssignmentError(list_item_id, worker_id)
            # 予期しないIntegrityErrorは再送出（ログ出力推奨）
            raise

        return self._to_entity(assignment)

    async def find_by_id(
        self,
        assignment_id: int,
        requesting_organization_id: int,
    ) -> ListItemAssignmentEntity | None:
        """IDで割り当てを検索（マルチテナント対応・IDOR脆弱性対策）"""
        # assignment -> list_item -> list -> organization を経由してテナント分離
        stmt = (
            select(ListItemAssignment)
            .join(ListItem, ListItemAssignment.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemAssignment.id == assignment_id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),  # 論理削除されたリスト項目を除外（一貫性のため）
            )
        )
        result = await self._session.execute(stmt)
        assignment = result.scalar_one_or_none()

        if assignment is None:
            return None

        return self._to_entity(assignment)

    async def list_by_list_item_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """リスト項目に割り当てられたワーカーの一覧を取得（マルチテナント対応）"""
        # assignment -> list_item -> list -> organization を経由してテナント分離
        stmt = (
            select(ListItemAssignment)
            .join(ListItem, ListItemAssignment.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemAssignment.list_item_id == list_item_id,
                List.organization_id == requesting_organization_id,
                ListItem.deleted_at.is_(None),
            )
            .order_by(ListItemAssignment.created_at.desc())
        )
        result = await self._session.execute(stmt)
        assignments = result.scalars().all()

        return [self._to_entity(assignment) for assignment in assignments]

    async def list_by_worker_id(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """ワーカーに割り当てられたリスト項目の一覧を取得（マルチテナント対応）"""
        # assignment -> worker と assignment -> list_item -> list -> organization
        # の両方でテナント分離を行う
        stmt = (
            select(ListItemAssignment)
            .join(Worker, ListItemAssignment.worker_id == Worker.id)
            .join(ListItem, ListItemAssignment.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemAssignment.worker_id == worker_id,
                Worker.organization_id == requesting_organization_id,
                List.organization_id == requesting_organization_id,
                Worker.deleted_at.is_(None),
                ListItem.deleted_at.is_(None),
            )
            .order_by(ListItemAssignment.created_at.desc())
        )
        result = await self._session.execute(stmt)
        assignments = result.scalars().all()

        return [self._to_entity(assignment) for assignment in assignments]

    async def unassign_worker_from_list_item(
        self,
        assignment_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        リスト項目からワーカーの割り当てを解除（物理削除）

        割り当てテーブルは中間テーブルのため、論理削除ではなく物理削除を行います。
        """
        # assignment -> list_item -> list -> organization を経由してテナント分離
        stmt = (
            select(ListItemAssignment)
            .join(ListItem, ListItemAssignment.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemAssignment.id == assignment_id,
                List.organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        assignment = result.scalar_one_or_none()

        if assignment is None:
            logger.warning(
                "Assignment not found or access denied for unassignment",
                extra={
                    "assignment_id": assignment_id,
                    "organization_id": requesting_organization_id,
                },
            )
            raise ListItemAssignmentNotFoundError(assignment_id)

        logger.info(
            "Unassigning worker from list item",
            extra={
                "assignment_id": assignment_id,
                "list_item_id": assignment.list_item_id,
                "worker_id": assignment.worker_id,
                "organization_id": requesting_organization_id,
            },
        )

        await self._session.delete(assignment)
        await self._session.flush()

    async def check_duplicate_assignment(
        self,
        list_item_id: int,
        worker_id: int,
        requesting_organization_id: int,
    ) -> bool:
        """
        重複割り当てをチェック

        assign_worker_to_list_item実行前のバリデーションに使用できます。
        """
        # assignment -> list_item -> list -> organization を経由してテナント分離
        stmt = (
            select(ListItemAssignment)
            .join(ListItem, ListItemAssignment.list_item_id == ListItem.id)
            .join(List, ListItem.list_id == List.id)
            .where(
                ListItemAssignment.list_item_id == list_item_id,
                ListItemAssignment.worker_id == worker_id,
                List.organization_id == requesting_organization_id,
            )
        )
        result = await self._session.execute(stmt)
        assignment = result.scalar_one_or_none()

        return assignment is not None

    async def assign_workers_to_list_in_bulk(
        self,
        list_id: int,
        worker_id: int,
        count: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        リスト内の未割り当て項目に対してワーカーを一括割り当て

        実装手順:
        1. リストの存在確認 + テナント分離
        2. ワーカーの存在確認 + テナント分離
        3. 未割り当てのリスト項目を取得（論理削除済みを除外）
        4. 指定件数分をワーカーに割り当て
        5. 一括INSERTで効率化
        """
        from src.domain.exceptions import ListNotFoundError

        logger.info(
            "Bulk assignment requested",
            extra={
                "list_id": list_id,
                "worker_id": worker_id,
                "count": count,
                "organization_id": requesting_organization_id,
            },
        )

        # マルチテナント対応: リストの所属組織を検証
        list_stmt = select(List).where(
            List.id == list_id,
            List.organization_id == requesting_organization_id,
            List.deleted_at.is_(None),
        )
        list_result = await self._session.execute(list_stmt)
        list_obj = list_result.scalar_one_or_none()

        if list_obj is None:
            logger.warning(
                "List not found or access denied",
                extra={
                    "list_id": list_id,
                    "organization_id": requesting_organization_id,
                },
            )
            raise ListNotFoundError(list_id)

        # マルチテナント対応: ワーカーの所属組織を検証
        worker_stmt = select(Worker).where(
            Worker.id == worker_id,
            Worker.organization_id == requesting_organization_id,
            Worker.deleted_at.is_(None),
        )
        worker_result = await self._session.execute(worker_stmt)
        worker = worker_result.scalar_one_or_none()

        if worker is None:
            logger.warning(
                "Worker not found or access denied",
                extra={
                    "worker_id": worker_id,
                    "organization_id": requesting_organization_id,
                },
            )
            raise WorkerNotFoundError(worker_id)

        # 未割り当てのリスト項目を取得
        # リスト項目から既に割り当てられている項目を除外するサブクエリ
        assigned_list_item_ids_subquery = (
            select(ListItemAssignment.list_item_id)
            .where(ListItemAssignment.worker_id == worker_id)
            .scalar_subquery()
        )

        # 未割り当てのリスト項目を取得（論理削除済みを除外）
        unassigned_items_stmt = (
            select(ListItem)
            .where(
                ListItem.list_id == list_id,
                ListItem.deleted_at.is_(None),
                ListItem.id.notin_(assigned_list_item_ids_subquery),
            )
            .order_by(ListItem.id)
            .limit(count)
        )
        unassigned_items_result = await self._session.execute(unassigned_items_stmt)
        unassigned_items = unassigned_items_result.scalars().all()

        # 未割り当て項目がない場合は空リストを返す
        if not unassigned_items:
            return []

        # 一括割り当て（効率的な一括INSERT）
        assignments_to_create = [
            ListItemAssignment(
                list_item_id=item.id,
                worker_id=worker_id,
            )
            for item in unassigned_items
        ]

        self._session.add_all(assignments_to_create)
        await self._session.flush()

        # 作成された割り当てをrefreshして最新の状態を取得
        for assignment in assignments_to_create:
            await self._session.refresh(assignment)

        logger.info(
            "Bulk assignment completed",
            extra={
                "list_id": list_id,
                "worker_id": worker_id,
                "requested_count": count,
                "assigned_count": len(assignments_to_create),
                "organization_id": requesting_organization_id,
            },
        )

        return [self._to_entity(assignment) for assignment in assignments_to_create]

    def _to_entity(self, assignment: ListItemAssignment) -> ListItemAssignmentEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return ListItemAssignmentEntity(
            id=assignment.id,
            list_item_id=assignment.list_item_id,
            worker_id=assignment.worker_id,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )
