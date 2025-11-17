"""
リスト項目リポジトリインターフェース

ドメイン層で定義するリスト項目リポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.list_item_entity import ListItemEntity


class IListItemRepository(ABC):
    """
    リスト項目リポジトリインターフェース

    営業先企業情報（リスト項目）の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        list_id: int,
        title: str,
        status: str = "pending",
    ) -> ListItemEntity:
        """
        リスト項目を作成

        Args:
            list_id: リストID
            title: 企業名などのタイトル
            status: ステータス（デフォルト: pending）

        Returns:
            ListItemEntity: 作成されたリスト項目エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> ListItemEntity | None:
        """
        IDでリスト項目を検索（マルチテナント対応）

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemEntity | None: 見つかった場合はリスト項目エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
            list -> organizationを経由してテナント分離します。
        """
        pass

    @abstractmethod
    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ListItemEntity]:
        """
        リストに属するリスト項目の一覧を取得（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済みリスト項目を含めるか

        Returns:
            list[ListItemEntity]: リスト項目エンティティのリスト

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def update(
        self,
        list_item: ListItemEntity,
        requesting_organization_id: int,
    ) -> ListItemEntity:
        """
        リスト項目情報を更新（マルチテナント対応）

        Args:
            list_item: 更新するリスト項目エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemEntity: 更新されたリスト項目エンティティ

        Raises:
            ListItemNotFoundError: リスト項目が見つからない場合、
                                  またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        list_item_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        リスト項目を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ListItemNotFoundError: リスト項目が見つからない場合、
                                  またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass
