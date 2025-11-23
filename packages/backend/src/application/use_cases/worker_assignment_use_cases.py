"""
ワーカー割り当てユースケース

ワーカーに割り当てられたリスト項目の管理を行います。
"""
from src.domain.entities.list_item_assignment_entity import ListItemAssignmentEntity
from src.domain.interfaces.list_item_assignment_repository import IListItemAssignmentRepository


class WorkerAssignmentUseCases:
    """ワーカー割り当てユースケースクラス"""

    def __init__(
        self,
        list_item_assignment_repository: IListItemAssignmentRepository,
    ) -> None:
        """
        Args:
            list_item_assignment_repository: リスト項目割り当てリポジトリ
        """
        self._assignment_repo = list_item_assignment_repository

    async def get_worker_assignments(
        self,
        worker_id: int,
        organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        ワーカーに割り当てられたリスト項目の一覧を取得

        Args:
            worker_id: ワーカーID
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            割り当てエンティティのリスト
        """
        assignments = await self._assignment_repo.list_by_worker_id(
            worker_id=worker_id,
            requesting_organization_id=organization_id,
        )
        return assignments
