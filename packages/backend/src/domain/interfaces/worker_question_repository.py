"""
ワーカー質問リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.worker_question_entity import WorkerQuestionEntity


class IWorkerQuestionRepository(ABC):
    """
    ワーカー質問リポジトリインターフェース

    ワーカー質問の永続化操作を定義します。
    """

    @abstractmethod
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
        """
        ワーカー質問を作成

        Args:
            worker_id: ワーカーID
            organization_id: 営業支援会社の組織ID（マルチテナントキー）
            title: 質問タイトル
            content: 質問内容
            client_organization_id: 顧客組織ID（オプション）
            status: ステータス（デフォルト: pending）
            priority: 優先度（デフォルト: medium）
            tags: タグ（JSON配列形式、オプション）

        Returns:
            WorkerQuestionEntity: 作成されたワーカー質問エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        question_id: int,
        requesting_organization_id: int,
    ) -> WorkerQuestionEntity | None:
        """
        IDでワーカー質問を検索（マルチテナント対応）

        Args:
            question_id: 質問ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            WorkerQuestionEntity | None: 見つかった場合は質問エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
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
        """
        営業支援会社に属するワーカー質問の一覧を取得

        Args:
            organization_id: 営業支援会社の組織ID
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            worker_id: フィルタ用のワーカーID（Noneの場合は全ワーカー）
            client_organization_id: フィルタ用の顧客組織ID（Noneの場合は全顧客）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み質問を含めるか

        Returns:
            list[WorkerQuestionEntity]: ワーカー質問エンティティのリスト
        """
        pass

    @abstractmethod
    async def list_by_worker(
        self,
        worker_id: int,
        organization_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[WorkerQuestionEntity]:
        """
        特定のワーカーの質問一覧を取得（マルチテナント対応）

        Args:
            worker_id: ワーカーID
            organization_id: 営業支援会社の組織ID（テナント分離用）
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み質問を含めるか

        Returns:
            list[WorkerQuestionEntity]: ワーカー質問エンティティのリスト

        Note:
            IDOR脆弱性対策として、organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def count_by_organization(
        self,
        organization_id: int,
        status: str | None = None,
        worker_id: int | None = None,
        client_organization_id: int | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        営業支援会社に属するワーカー質問の総件数を取得

        Args:
            organization_id: 営業支援会社の組織ID
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            worker_id: フィルタ用のワーカーID（Noneの場合は全ワーカー）
            client_organization_id: フィルタ用の顧客組織ID（Noneの場合は全顧客）
            include_deleted: 削除済み質問を含めるか

        Returns:
            int: ワーカー質問の総件数
        """
        pass

    @abstractmethod
    async def count_by_worker(
        self,
        worker_id: int,
        organization_id: int,
        status: str | None = None,
        include_deleted: bool = False,
    ) -> int:
        """
        特定のワーカーの質問総件数を取得（マルチテナント対応）

        Args:
            worker_id: ワーカーID
            organization_id: 営業支援会社の組織ID（テナント分離用）
            status: フィルタ用のステータス（Noneの場合は全ステータス）
            include_deleted: 削除済み質問を含めるか

        Returns:
            int: ワーカー質問の総件数

        Note:
            IDOR脆弱性対策として、organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def update(
        self,
        question: WorkerQuestionEntity,
        requesting_organization_id: int,
    ) -> WorkerQuestionEntity:
        """
        ワーカー質問情報を更新（マルチテナント対応）

        Args:
            question: 更新するワーカー質問エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            WorkerQuestionEntity: 更新されたワーカー質問エンティティ

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合、
                                        またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def add_answer(
        self,
        question_id: int,
        requesting_organization_id: int,
        answer: str,
        answered_by_user_id: int,
    ) -> WorkerQuestionEntity:
        """
        ワーカー質問に回答を追加（マルチテナント対応）

        Args:
            question_id: 質問ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            answer: 回答内容
            answered_by_user_id: 回答者のユーザーID

        Returns:
            WorkerQuestionEntity: 更新されたワーカー質問エンティティ

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合、
                                        またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            回答追加時に、statusを自動的に"answered"に変更し、answered_atに現在時刻を設定します。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        question_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        ワーカー質問を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            question_id: 質問ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            WorkerQuestionNotFoundError: 質問が見つからない場合、
                                        またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass
