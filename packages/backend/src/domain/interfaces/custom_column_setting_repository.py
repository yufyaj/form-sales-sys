"""
カスタムカラム設定リポジトリインターフェース

ドメイン層で定義するカスタムカラム設定リポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.custom_column_setting_entity import CustomColumnSettingEntity


class ICustomColumnSettingRepository(ABC):
    """
    カスタムカラム設定リポジトリインターフェース

    リストのカスタムカラム設定の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        list_id: int,
        column_name: str,
        display_name: str,
        column_config: dict,
        display_order: int,
    ) -> CustomColumnSettingEntity:
        """
        カスタムカラム設定を作成

        Args:
            list_id: リストID
            column_name: カラム識別子
            display_name: カラム表示名
            column_config: カラム設定（型、検証ルール、オプションなど）
            display_order: 表示順序

        Returns:
            CustomColumnSettingEntity: 作成されたカスタムカラム設定エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        custom_column_setting_id: int,
        requesting_organization_id: int,
    ) -> CustomColumnSettingEntity | None:
        """
        IDでカスタムカラム設定を検索（マルチテナント対応）

        Args:
            custom_column_setting_id: カスタムカラム設定ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            CustomColumnSettingEntity | None: 見つかった場合はカスタムカラム設定エンティティ、見つからない場合はNone

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
            custom_column_setting -> list -> organizationを経由してテナント分離します。
        """
        pass

    @abstractmethod
    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[CustomColumnSettingEntity]:
        """
        リストに属するカスタムカラム設定の一覧を取得（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            include_deleted: 削除済みカスタムカラム設定を含めるか

        Returns:
            list[CustomColumnSettingEntity]: カスタムカラム設定エンティティのリスト（表示順序でソート済み）

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def update(
        self,
        custom_column_setting: CustomColumnSettingEntity,
        requesting_organization_id: int,
    ) -> CustomColumnSettingEntity:
        """
        カスタムカラム設定情報を更新（マルチテナント対応）

        Args:
            custom_column_setting: 更新するカスタムカラム設定エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            CustomColumnSettingEntity: 更新されたカスタムカラム設定エンティティ

        Raises:
            CustomColumnSettingNotFoundError: カスタムカラム設定が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        custom_column_setting_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        カスタムカラム設定を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            custom_column_setting_id: カスタムカラム設定ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            CustomColumnSettingNotFoundError: カスタムカラム設定が見つからない場合、
                                             またはrequesting_organization_idと一致しない場合

        Note:
            IDOR脆弱性対策として、requesting_organization_idで必ずテナント分離を行います。
        """
        pass
