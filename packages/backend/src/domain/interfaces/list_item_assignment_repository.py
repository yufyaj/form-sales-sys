"""
リスト項目割り当てリポジトリインターフェース

ドメイン層で定義するリスト項目割り当てリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.list_item_assignment_entity import ListItemAssignmentEntity


class IListItemAssignmentRepository(ABC):
    """
    リスト項目割り当てリポジトリインターフェース

    リスト項目とワーカーの割り当て関係の永続化操作を定義します。
    重複割り当て防止ロジックを含みます。
    """

    @abstractmethod
    async def assign_worker_to_list_item(
        self,
        list_item_id: int,
        worker_id: int,
        requesting_organization_id: int,
    ) -> ListItemAssignmentEntity:
        """
        リスト項目にワーカーを割り当て

        Args:
            list_item_id: リスト項目ID
            worker_id: ワーカーID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemAssignmentEntity: 作成された割り当てエンティティ

        Raises:
            DuplicateAssignmentError: 既に同じリスト項目に同じワーカーが割り当てられている場合
            ListItemNotFoundError: リスト項目が見つからない場合、
                                  またはrequesting_organization_idと一致しない場合
            WorkerNotFoundError: ワーカーが見つからない場合、
                                またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            重複割り当ては、データベースの複合ユニーク制約（uq_list_item_worker）で防止されます。
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        assignment_id: int,
        requesting_organization_id: int,
    ) -> ListItemAssignmentEntity | None:
        """
        IDで割り当てを検索（マルチテナント対応）

        Args:
            assignment_id: 割り当てID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemAssignmentEntity | None: 見つかった場合は割り当てエンティティ、見つからない場合はNone

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_list_item_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        リスト項目に割り当てられたワーカーの一覧を取得（マルチテナント対応）

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            list[ListItemAssignmentEntity]: 割り当てエンティティのリスト

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_worker_id(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        ワーカーに割り当てられたリスト項目の一覧を取得（マルチテナント対応）

        Args:
            worker_id: ワーカーID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            list[ListItemAssignmentEntity]: 割り当てエンティティのリスト

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def unassign_worker_from_list_item(
        self,
        assignment_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        リスト項目からワーカーの割り当てを解除（物理削除）

        Args:
            assignment_id: 割り当てID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            AssignmentNotFoundError: 割り当てが見つからない場合、
                                    またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            割り当てテーブルは中間テーブルのため、論理削除ではなく物理削除を行います。
        """
        pass

    @abstractmethod
    async def check_duplicate_assignment(
        self,
        list_item_id: int,
        worker_id: int,
        requesting_organization_id: int,
    ) -> bool:
        """
        重複割り当てをチェック

        Args:
            list_item_id: リスト項目ID
            worker_id: ワーカーID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            bool: 既に割り当てられている場合True、そうでない場合False

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            このメソッドは、assign_worker_to_list_item実行前のバリデーションに使用できます。
        """
        pass

    @abstractmethod
    async def assign_workers_to_list_in_bulk(
        self,
        list_id: int,
        worker_id: int,
        count: int,
        requesting_organization_id: int,
    ) -> list[ListItemAssignmentEntity]:
        """
        リスト内の未割り当て項目に対してワーカーを一括割り当て

        Args:
            list_id: リストID
            worker_id: ワーカーID
            count: 割り当て件数（1以上）
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            list[ListItemAssignmentEntity]: 作成された割り当てエンティティのリスト

        Raises:
            ListNotFoundError: リストが見つからない場合、
                              またはrequesting_organization_idと一致しない場合
            WorkerNotFoundError: ワーカーが見つからない場合、
                                またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            既に割り当て済みのリスト項目は除外されます。
            論理削除されたリスト項目も除外されます。
            未割り当て項目がcount未満の場合、利用可能な全項目を割り当てます。
        """
        pass
