"""
送信不可理由リポジトリインターフェース

ドメイン層で定義するリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity


class ICannotSendReasonRepository(ABC):
    """
    送信不可理由リポジトリインターフェース

    送信不可理由マスターデータの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        reason_code: str,
        reason_name: str,
        description: str | None = None,
        is_active: bool = True,
    ) -> CannotSendReasonEntity:
        """
        送信不可理由を作成

        Args:
            reason_code: 理由コード（例: FORM_NOT_FOUND, CAPTCHA_REQUIRED）
            reason_name: 理由名
            description: 詳細説明
            is_active: 有効/無効フラグ

        Returns:
            CannotSendReasonEntity: 作成された送信不可理由エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        reason_id: int,
    ) -> CannotSendReasonEntity | None:
        """
        IDで送信不可理由を検索

        Args:
            reason_id: 送信不可理由ID

        Returns:
            CannotSendReasonEntity | None: 見つかった場合は送信不可理由エンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def find_by_reason_code(
        self,
        reason_code: str,
    ) -> CannotSendReasonEntity | None:
        """
        理由コードで送信不可理由を検索

        Args:
            reason_code: 理由コード

        Returns:
            CannotSendReasonEntity | None: 見つかった場合は送信不可理由エンティティ、見つからない場合はNone
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        is_active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[CannotSendReasonEntity]:
        """
        送信不可理由の一覧を取得

        Args:
            is_active_only: 有効な理由のみを取得するか
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み理由を含めるか

        Returns:
            list[CannotSendReasonEntity]: 送信不可理由エンティティのリスト
        """
        pass

    @abstractmethod
    async def count_all(
        self,
        is_active_only: bool = True,
        include_deleted: bool = False,
    ) -> int:
        """
        送信不可理由の総件数を取得

        Args:
            is_active_only: 有効な理由のみをカウントするか
            include_deleted: 削除済み理由を含めるか

        Returns:
            int: 送信不可理由の総件数
        """
        pass

    @abstractmethod
    async def update(
        self,
        reason: CannotSendReasonEntity,
    ) -> CannotSendReasonEntity:
        """
        送信不可理由を更新

        Args:
            reason: 更新する送信不可理由エンティティ

        Returns:
            CannotSendReasonEntity: 更新された送信不可理由エンティティ

        Raises:
            CannotSendReasonNotFoundError: 送信不可理由が見つからない場合
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        reason_id: int,
    ) -> None:
        """
        送信不可理由を論理削除（ソフトデリート）

        Args:
            reason_id: 送信不可理由ID

        Raises:
            CannotSendReasonNotFoundError: 送信不可理由が見つからない場合
        """
        pass
