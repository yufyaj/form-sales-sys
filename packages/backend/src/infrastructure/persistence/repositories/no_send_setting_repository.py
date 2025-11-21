"""
送信禁止設定リポジトリの実装

INoSendSettingRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, date, time, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.no_send_setting_entity import NoSendSettingEntity, NoSendSettingType
from src.domain.exceptions import NoSendSettingNotFoundError
from src.domain.interfaces.no_send_setting_repository import INoSendSettingRepository
from src.infrastructure.persistence.models.no_send_setting import NoSendSetting
from src.infrastructure.persistence.models.list import List


class NoSendSettingRepository(INoSendSettingRepository):
    """
    送信禁止設定リポジトリの実装

    SQLAlchemyを使用して送信禁止設定の永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

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
        """送信禁止設定を作成"""
        no_send_setting_model = NoSendSetting(
            list_id=list_id,
            setting_type=setting_type.value,
            name=name,
            description=description,
            is_enabled=is_enabled,
            day_of_week_list=day_of_week_list,
            time_start=time_start,
            time_end=time_end,
            specific_date=specific_date,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
        )

        self._session.add(no_send_setting_model)
        await self._session.flush()
        await self._session.refresh(no_send_setting_model)

        return self._to_entity(no_send_setting_model)

    async def find_by_id(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> NoSendSettingEntity | None:
        """IDで送信禁止設定を検索（マルチテナント対応・IDOR脆弱性対策）"""
        # JOINしてリストの所属組織を確認
        stmt = (
            select(NoSendSetting)
            .join(List, NoSendSetting.list_id == List.id)
            .where(
                NoSendSetting.id == no_send_setting_id,
                List.organization_id == requesting_organization_id,
                NoSendSetting.deleted_at.is_(None),
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        no_send_setting_model = result.scalar_one_or_none()

        if no_send_setting_model is None:
            return None

        return self._to_entity(no_send_setting_model)

    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_disabled: bool = False,
        include_deleted: bool = False,
    ) -> list[NoSendSettingEntity]:
        """リストIDに紐づく送信禁止設定の一覧を取得（マルチテナント対応）"""
        # JOINしてリストの所属組織を確認
        conditions = [
            NoSendSetting.list_id == list_id,
            List.organization_id == requesting_organization_id,
            List.deleted_at.is_(None),
        ]

        if not include_disabled:
            conditions.append(NoSendSetting.is_enabled.is_(True))

        if not include_deleted:
            conditions.append(NoSendSetting.deleted_at.is_(None))

        stmt = (
            select(NoSendSetting)
            .join(List, NoSendSetting.list_id == List.id)
            .where(and_(*conditions))
            .order_by(NoSendSetting.created_at.desc())
        )

        result = await self._session.execute(stmt)
        no_send_settings = result.scalars().all()

        return [self._to_entity(setting) for setting in no_send_settings]

    async def update(
        self,
        no_send_setting_entity: NoSendSettingEntity,
        requesting_organization_id: int,
    ) -> NoSendSettingEntity:
        """送信禁止設定を更新（マルチテナント対応・IDOR脆弱性対策）"""
        # JOINしてリストの所属組織を確認
        stmt = (
            select(NoSendSetting)
            .join(List, NoSendSetting.list_id == List.id)
            .where(
                NoSendSetting.id == no_send_setting_entity.id,
                List.organization_id == requesting_organization_id,
                NoSendSetting.deleted_at.is_(None),
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_no_send_setting = result.scalar_one_or_none()

        if db_no_send_setting is None:
            raise NoSendSettingNotFoundError(no_send_setting_entity.id)

        # エンティティの値でモデルを更新
        db_no_send_setting.setting_type = no_send_setting_entity.setting_type.value
        db_no_send_setting.name = no_send_setting_entity.name
        db_no_send_setting.description = no_send_setting_entity.description
        db_no_send_setting.is_enabled = no_send_setting_entity.is_enabled
        db_no_send_setting.day_of_week_list = no_send_setting_entity.day_of_week_list
        db_no_send_setting.time_start = no_send_setting_entity.time_start
        db_no_send_setting.time_end = no_send_setting_entity.time_end
        db_no_send_setting.specific_date = no_send_setting_entity.specific_date
        db_no_send_setting.date_range_start = no_send_setting_entity.date_range_start
        db_no_send_setting.date_range_end = no_send_setting_entity.date_range_end

        await self._session.flush()
        await self._session.refresh(db_no_send_setting)

        return self._to_entity(db_no_send_setting)

    async def soft_delete(
        self,
        no_send_setting_id: int,
        requesting_organization_id: int,
    ) -> None:
        """送信禁止設定を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        # JOINしてリストの所属組織を確認
        stmt = (
            select(NoSendSetting)
            .join(List, NoSendSetting.list_id == List.id)
            .where(
                NoSendSetting.id == no_send_setting_id,
                List.organization_id == requesting_organization_id,
                NoSendSetting.deleted_at.is_(None),
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        no_send_setting_model = result.scalar_one_or_none()

        if no_send_setting_model is None:
            raise NoSendSettingNotFoundError(no_send_setting_id)

        no_send_setting_model.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(self, no_send_setting_model: NoSendSetting) -> NoSendSettingEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return NoSendSettingEntity(
            id=no_send_setting_model.id,
            list_id=no_send_setting_model.list_id,
            setting_type=NoSendSettingType(no_send_setting_model.setting_type),
            name=no_send_setting_model.name,
            description=no_send_setting_model.description,
            is_enabled=no_send_setting_model.is_enabled,
            day_of_week_list=no_send_setting_model.day_of_week_list,
            time_start=no_send_setting_model.time_start,
            time_end=no_send_setting_model.time_end,
            specific_date=no_send_setting_model.specific_date,
            date_range_start=no_send_setting_model.date_range_start,
            date_range_end=no_send_setting_model.date_range_end,
            created_at=no_send_setting_model.created_at,
            updated_at=no_send_setting_model.updated_at,
            deleted_at=no_send_setting_model.deleted_at,
        )
