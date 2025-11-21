"""
リストリポジトリインターフェース

ドメイン層で定義するリストリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.list_entity import ListEntity


class IListRepository(ABC):
    """
    リストリポジトリインターフェース

    営業先企業リストの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        organization_id: int,
        name: str,
        description: str | None = None,
    ) -> ListEntity:
        """
        リストを作成

        Args:
            organization_id: 営業支援会社の組織ID
            name: リスト名
            description: リストの説明

        Returns:
            ListEntity: 作成されたリストエンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> ListEntity | None:
        """
        IDでリストを検索（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListEntity | None: 見つかった場合はリストエンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def list_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ListEntity]:
        """
        組織に属するリストの一覧を取得

        Args:
            organization_id: 営業支援会社の組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済みリストを含めるか

        Returns:
            list[ListEntity]: リストエンティティのリスト
        """
        pass

    @abstractmethod
    async def update(
        self,
        list_entity: ListEntity,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        リスト情報を更新（マルチテナント対応）

        Args:
            list_entity: 更新するリストエンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListEntity: 更新されたリストエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合、
                              またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        リストを論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ListNotFoundError: リストが見つからない場合、
                              またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def duplicate(
        self,
        source_list_id: int,
        new_name: str,
        requesting_organization_id: int,
    ) -> ListEntity:
        """
        リストを複製

        Args:
            source_list_id: 複製元のリストID
            new_name: 新しいリスト名
            requesting_organization_id: リクエスト元の組織ID（テナント分離用）

        Returns:
            ListEntity: 複製されたリストエンティティ

        Raises:
            ListNotFoundError: 複製元のリストが見つからない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            リストに紐づくリストアイテム（list_items）とカスタム値（list_item_custom_values）も一緒に複製します。
        """
        pass
