"""
作業記録リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.domain.entities.work_record_entity import WorkRecordEntity
from src.infrastructure.persistence.models.work_record import WorkRecordStatus


class IWorkRecordRepository(ABC):
    """
    作業記録リポジトリインターフェース

    作業記録の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        assignment_id: int,
        worker_id: int,
        status: WorkRecordStatus,
        started_at: datetime,
        completed_at: datetime,
        form_submission_result: dict[str, Any] | None = None,
        cannot_send_reason_id: int | None = None,
        notes: str | None = None,
    ) -> WorkRecordEntity:
        """
        作業記録を作成

        Args:
            assignment_id: リスト項目割り当てID
            worker_id: ワーカーID
            status: 送信済み or 送信不可
            started_at: 作業開始日時
            completed_at: 作業完了日時
            form_submission_result: 送信結果の詳細（JSON）
            cannot_send_reason_id: 送信不可理由ID（送信不可の場合のみ）
            notes: メモ・備考

        Returns:
            WorkRecordEntity: 作成された作業記録エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        record_id: int,
    ) -> WorkRecordEntity | None:
        """
        IDで作業記録を検索

        Args:
            record_id: 作業記録ID

        Returns:
            WorkRecordEntity | None: 見つかった場合は作業記録エンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_assignment_id(
        self,
        assignment_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """
        割り当てIDで作業記録を検索

        Args:
            assignment_id: リスト項目割り当てID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み記録を含めるか

        Returns:
            list[WorkRecordEntity]: 作業記録エンティティのリスト
        """
        pass

    @abstractmethod
    async def find_by_worker_id(
        self,
        worker_id: int,
        status: WorkRecordStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """
        ワーカーIDで作業記録を検索

        Args:
            worker_id: ワーカーID
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            start_date: 検索開始日時（completed_at基準）
            end_date: 検索終了日時（completed_at基準）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み記録を含めるか

        Returns:
            list[WorkRecordEntity]: 作業記録エンティティのリスト
        """
        pass

    @abstractmethod
    async def count_by_worker_id(
        self,
        worker_id: int,
        status: WorkRecordStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        ワーカーIDで作業記録の件数をカウント

        Args:
            worker_id: ワーカーID
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            start_date: 検索開始日時（completed_at基準）
            end_date: 検索終了日時（completed_at基準）
            include_deleted: 削除済み記録を含めるか

        Returns:
            int: 作業記録の件数
        """
        pass

    @abstractmethod
    async def list_by_status(
        self,
        status: WorkRecordStatus,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkRecordEntity]:
        """
        ステータスで作業記録を検索

        Args:
            status: 検索するステータス
            start_date: 検索開始日時（completed_at基準）
            end_date: 検索終了日時（completed_at基準）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み記録を含めるか

        Returns:
            list[WorkRecordEntity]: 作業記録エンティティのリスト
        """
        pass

    @abstractmethod
    async def update(
        self,
        record: WorkRecordEntity,
    ) -> WorkRecordEntity:
        """
        作業記録を更新

        Args:
            record: 更新する作業記録エンティティ

        Returns:
            WorkRecordEntity: 更新された作業記録エンティティ

        Raises:
            WorkRecordNotFoundError: 作業記録が見つからない場合
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        record_id: int,
    ) -> None:
        """
        作業記録を論理削除（ソフトデリート）

        Args:
            record_id: 作業記録ID

        Raises:
            WorkRecordNotFoundError: 作業記録が見つからない場合
        """
        pass

    @abstractmethod
    async def find_by_id_with_access_check(
        self,
        record_id: int,
        requesting_worker_id: int,
        requesting_organization_id: int,
    ) -> WorkRecordEntity | None:
        """
        IDで作業記録を検索（アクセス権限チェック付き）

        マルチテナント環境でのIDOR（Insecure Direct Object Reference）脆弱性対策として、
        リクエストしているワーカーが同じ組織に所属している場合のみアクセスを許可します。

        Args:
            record_id: 作業記録ID
            requesting_worker_id: リクエストしているワーカーID
            requesting_organization_id: リクエストしている組織ID

        Returns:
            WorkRecordEntity | None: アクセス権限がある場合は作業記録エンティティ、
                                      権限がない場合やデータが存在しない場合はNone

        Note:
            セキュリティ上、データが存在しないのか権限がないのかを区別せず、
            両方ともNoneを返します（情報漏洩防止）
        """
        pass
