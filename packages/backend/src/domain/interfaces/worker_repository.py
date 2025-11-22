"""
ワーカーリポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.worker_entity import WorkerEntity
from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus


class IWorkerRepository(ABC):
    """
    ワーカーリポジトリインターフェース

    ワーカーの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        user_id: int,
        organization_id: int,
        status: WorkerStatus = WorkerStatus.PENDING,
        skill_level: SkillLevel | None = None,
        experience_months: int | None = None,
        specialties: str | None = None,
        max_tasks_per_day: int | None = None,
        available_hours_per_week: int | None = None,
        notes: str | None = None,
    ) -> WorkerEntity:
        """
        ワーカーを作成

        Args:
            user_id: 対応するUserのID
            organization_id: 営業支援会社の組織ID
            status: ワーカーステータス
            skill_level: スキルレベル
            experience_months: 経験月数
            specialties: 得意分野・専門領域
            max_tasks_per_day: 1日の最大タスク数
            available_hours_per_week: 週間稼働可能時間
            notes: 管理者用メモ・備考

        Returns:
            WorkerEntity: 作成されたワーカーエンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> WorkerEntity | None:
        """
        IDでワーカーを検索（マルチテナント対応）

        Args:
            worker_id: ワーカーID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            WorkerEntity | None: 見つかった場合はワーカーエンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: int,
        requesting_organization_id: int,
    ) -> WorkerEntity | None:
        """
        ユーザーIDでワーカーを検索（マルチテナント対応）

        Args:
            user_id: ユーザーID（users.id）
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            WorkerEntity | None: 見つかった場合はワーカーエンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: int,
        status: WorkerStatus | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkerEntity]:
        """
        営業支援会社に属するワーカーの一覧を取得

        Args:
            organization_id: 営業支援会社の組織ID
            status: フィルタ用のワーカーステータス（Noneの場合は全ステータス）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済みワーカーを含めるか

        Returns:
            list[WorkerEntity]: ワーカーエンティティのリスト
        """
        pass

    @abstractmethod
    async def count_by_organization(
        self,
        organization_id: int,
        status: WorkerStatus | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        営業支援会社に属するワーカーの総件数を取得

        Args:
            organization_id: 営業支援会社の組織ID
            status: フィルタ用のワーカーステータス（Noneの場合は全ステータス）
            include_deleted: 削除済みワーカーを含めるか

        Returns:
            int: ワーカーの総件数
        """
        pass

    @abstractmethod
    async def update(
        self,
        worker: WorkerEntity,
        requesting_organization_id: int,
    ) -> WorkerEntity:
        """
        ワーカー情報を更新（マルチテナント対応）

        Args:
            worker: 更新するワーカーエンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            WorkerEntity: 更新されたワーカーエンティティ

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合、
                                またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        worker_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        ワーカーを論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            worker_id: ワーカーID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            WorkerNotFoundError: ワーカーが見つからない場合、
                                またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
