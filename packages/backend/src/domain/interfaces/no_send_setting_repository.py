"""
送信禁止設定リポジトリインターフェース

ドメイン層で定義する送信禁止設定リポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod
from datetime import date, time

from src.domain.entities.no_send_setting_entity import NoSendSettingEntity, NoSendSettingType


class INoSendSettingRepository(ABC):
    """
    送信禁止設定リポジトリインターフェース

    営業メール等の自動送信を禁止する時間帯・曜日・日付の設定の永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        list_id: int,
        setting_type: NoSendSettingType,
        name: str,
        description: str | None = None,
        is_enabled: bool = True,
        day_of_week_list: list[int] | None = None,
        time_start: time | None = None,
        time_end: time | None = None,
        specific_date: date | None = None,
        date_range_start: date | None = None,
        date_range_end: date | None = None,
    ) -> NoSendSettingEntity:
        """
        送信禁止設定を作成

        Args:
            list_id: リストID
            setting_type: 設定種別
            name: 設定名
            description: 設定の説明
            is_enabled: 有効/無効フラグ
            day_of_week_list: 送信禁止曜日リスト（setting_type=day_of_weekの場合）
            time_start: 送信禁止開始時刻（setting_type=time_rangeの場合）
            time_end: 送信禁止終了時刻（setting_type=time_rangeの場合）
            specific_date: 送信禁止日（setting_type=specific_dateの場合）
            date_range_start: 送信禁止期間開始日（setting_type=specific_dateの場合）
            date_range_end: 送信禁止期間終了日（setting_type=specific_dateの場合）

        Returns:
            NoSendSettingEntity: 作成された送信禁止設定エンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> NoSendSettingEntity | None:
        """
        IDで送信禁止設定を検索（マルチテナント対応）

        Args:
            no_send_setting_id: 送信禁止設定ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            NoSendSettingEntity | None: 見つかった場合は送信禁止設定エンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
            リストの所属組織を確認します。
        """
        pass

    @abstractmethod
    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_disabled: bool = False,
        include_deleted: bool = False,
    ) -> list[NoSendSettingEntity]:
        """
        リストIDに紐づく送信禁止設定の一覧を取得（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            include_disabled: 無効な設定を含めるか
            include_deleted: 削除済み設定を含めるか

        Returns:
            list[NoSendSettingEntity]: 送信禁止設定エンティティのリスト

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def update(
        self,
        no_send_setting_entity: NoSendSettingEntity,
        requesting_organization_id: int,
    ) -> NoSendSettingEntity:
        """
        送信禁止設定を更新（マルチテナント対応）

        Args:
            no_send_setting_entity: 更新する送信禁止設定エンティティ
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            NoSendSettingEntity: 更新された送信禁止設定エンティティ

        Raises:
            NoSendSettingNotFoundError: 送信禁止設定が見つからない場合、
                                       またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def soft_delete(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        送信禁止設定を論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            no_send_setting_id: 送信禁止設定ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            NoSendSettingNotFoundError: 送信禁止設定が見つからない場合、
                                       またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
