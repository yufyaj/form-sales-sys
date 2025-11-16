"""
リスト項目カスタム値リポジトリインターフェース

ドメイン層で定義するリスト項目カスタム値リポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.list_item_custom_value_entity import ListItemCustomValueEntity


class IListItemCustomValueRepository(ABC):
    """
    リスト項目カスタム値リポジトリインターフェース

    リスト項目のカスタムカラム値の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        list_item_id: int,
        custom_column_setting_id: int,
        value: dict | None = None,
    ) -> ListItemCustomValueEntity:
        """
        リスト項目カスタム値を作成

        Args:
            list_item_id: リスト項目ID
            custom_column_setting_id: カスタムカラム設定ID
            value: カスタムカラムの値

        Returns:
            ListItemCustomValueEntity: 作成されたリスト項目カスタム値エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        list_item_custom_value_id: int,
        requesting_organization_id: int,
    ) -> ListItemCustomValueEntity | None:
        """
        IDでリスト項目カスタム値を検索（マルチテナント対応）

        Args:
            list_item_custom_value_id: リスト項目カスタム値ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemCustomValueEntity | None: 見つかった場合はリスト項目カスタム値エンティティ、見つからない場合はNone

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            list_item_custom_value -> list_item -> list -> organizationを経由してテナント分離します。
        """
        pass

    @abstractmethod
    async def list_by_list_item_id(
        self,
        list_item_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[ListItemCustomValueEntity]:
        """
        リスト項目に属するカスタム値の一覧を取得（マルチテナント対応）

        Args:
            list_item_id: リスト項目ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            include_deleted: 削除済みカスタム値を含めるか

        Returns:
            list[ListItemCustomValueEntity]: リスト項目カスタム値エンティティのリスト

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def update(
        self,
        list_item_custom_value: ListItemCustomValueEntity,
        requesting_organization_id: int,
    ) -> ListItemCustomValueEntity:
        """
        リスト項目カスタム値を更新（マルチテナント対応）

        Args:
            list_item_custom_value: 更新するリスト項目カスタム値エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            ListItemCustomValueEntity: 更新されたリスト項目カスタム値エンティティ

        Raises:
            ListItemCustomValueNotFoundError: リスト項目カスタム値が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        list_item_custom_value_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        リスト項目カスタム値を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            list_item_custom_value_id: リスト項目カスタム値ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            ListItemCustomValueNotFoundError: リスト項目カスタム値が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass
