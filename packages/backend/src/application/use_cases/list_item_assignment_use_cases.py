"""
リスト項目割り当て管理のユースケース

リスト項目とワーカーの割り当て関係のビジネスロジックを実行します
"""

from src.domain.entities.list_item_assignment_entity import ListItemAssignmentEntity
from src.domain.interfaces.list_item_assignment_repository import (
    IListItemAssignmentRepository,
)


class ListItemAssignmentUseCases:
    """リスト項目割り当て管理のユースケースクラス"""

    def __init__(
        self,
        assignment_repository: IListItemAssignmentRepository,
    ) -> None:
        """
        Args:
            assignment_repository: リスト項目割り当てリポジトリ
        """
        self._assignment_repo = assignment_repository

    async def bulk_assign_workers_to_list(
        self,
        list_id: int,
        worker_id: int,
        count: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        リストへのワーカー一括割り当て

        Args:
            list_id: リストID
            worker_id: ワーカーID
            count: 割り当て件数
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            作成された割り当てエンティティのリスト

        Raises:
            ListNotFoundError: リストが見つからない場合、
                              またはrequesting_organization_idと一致しない場合
            WorkerNotFoundError: ワーカーが見つからない場合、
                                またはrequesting_organization_idと一致しない場合
        """
        assignments = await self._assignment_repo.assign_workers_to_list_in_bulk(
            list_id=list_id,
            worker_id=worker_id,
            count=count,
            requesting_organization_id=requesting_organization_id,
        )
        return assignments

    async def unassign_worker(
        self,
        assignment_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        割り当て解除

        Args:
            assignment_id: 割り当てID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ListItemAssignmentNotFoundError: 割り当てが見つからない場合、
                                            またはrequesting_organization_idと一致しない場合
        """
        await self._assignment_repo.unassign_worker_from_list_item(
            assignment_id=assignment_id,
            requesting_organization_id=requesting_organization_id,
        )
