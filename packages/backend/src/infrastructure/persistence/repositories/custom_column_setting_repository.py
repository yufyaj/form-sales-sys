"""
カスタムカラム設定リポジトリの実装

ICustomColumnSettingRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.custom_column_setting_entity import CustomColumnSettingEntity
from src.domain.exceptions import CustomColumnSettingNotFoundError
from src.domain.interfaces.custom_column_setting_repository import (
    ICustomColumnSettingRepository,
)
from src.infrastructure.persistence.models.custom_column_setting import (
    CustomColumnSetting,
)
from src.infrastructure.persistence.models.list import List


class CustomColumnSettingRepository(ICustomColumnSettingRepository):
    """
    カスタムカラム設定リポジトリの実装

    SQLAlchemyを使用してカスタムカラム設定の永続化を行います。
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
        column_name: str,
        display_name: str,
        column_config: dict,
        display_order: int,
    ) -> CustomColumnSettingEntity:
        """カスタムカラム設定を作成"""
        setting = CustomColumnSetting(
            list_id=list_id,
            column_name=column_name,
            display_name=display_name,
            column_config=column_config,
            display_order=display_order,
        )

        self._session.add(setting)
        await self._session.flush()
        await self._session.refresh(setting)

        return self._to_entity(setting)

    async def find_by_id(
        self,
        custom_column_setting_id: int,
        requesting_organization_id: int,
    ) -> CustomColumnSettingEntity | None:
        """IDでカスタムカラム設定を検索（マルチテナント対応・IDOR脆弱性対策）"""
        # custom_column_setting -> list -> organizationを経由してテナント分離
        stmt = (
            select(CustomColumnSetting)
            .join(List, CustomColumnSetting.list_id == List.id)
            .where(
                CustomColumnSetting.id == custom_column_setting_id,
                List.organization_id == requesting_organization_id,
                CustomColumnSetting.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        setting = result.scalar_one_or_none()

        if setting is None:
            return None

        return self._to_entity(setting)

    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[CustomColumnSettingEntity]:
        """リストに属するカスタムカラム設定の一覧を取得（マルチテナント対応）"""
        # custom_column_setting -> list -> organizationを経由してテナント分離
        conditions = [
            CustomColumnSetting.list_id == list_id,
            List.organization_id == requesting_organization_id,
        ]
        if not include_deleted:
            conditions.append(CustomColumnSetting.deleted_at.is_(None))

        stmt = (
            select(CustomColumnSetting)
            .join(List, CustomColumnSetting.list_id == List.id)
            .where(and_(*conditions))
            .order_by(CustomColumnSetting.display_order.asc())  # 表示順序でソート
        )

        result = await self._session.execute(stmt)
        settings = result.scalars().all()

        return [self._to_entity(s) for s in settings]

    async def update(
        self,
        custom_column_setting: CustomColumnSettingEntity,
        requesting_organization_id: int,
    ) -> CustomColumnSettingEntity:
        """カスタムカラム設定情報を更新（マルチテナント対応・IDOR脆弱性対策）"""
        # custom_column_setting -> list -> organizationを経由してテナント分離
        stmt = (
            select(CustomColumnSetting)
            .join(List, CustomColumnSetting.list_id == List.id)
            .where(
                CustomColumnSetting.id == custom_column_setting.id,
                List.organization_id == requesting_organization_id,
                CustomColumnSetting.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        db_setting = result.scalar_one_or_none()

        if db_setting is None:
            raise CustomColumnSettingNotFoundError(custom_column_setting.id)

        # エンティティの値でモデルを更新
        db_setting.column_name = custom_column_setting.column_name
        db_setting.display_name = custom_column_setting.display_name
        db_setting.column_config = custom_column_setting.column_config
        db_setting.display_order = custom_column_setting.display_order

        await self._session.flush()
        await self._session.refresh(db_setting)

        return self._to_entity(db_setting)

    async def soft_delete(
        self,
        custom_column_setting_id: int,
        requesting_organization_id: int,
    ) -> None:
        """カスタムカラム設定を論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        # custom_column_setting -> list -> organizationを経由してテナント分離
        stmt = (
            select(CustomColumnSetting)
            .join(List, CustomColumnSetting.list_id == List.id)
            .where(
                CustomColumnSetting.id == custom_column_setting_id,
                List.organization_id == requesting_organization_id,
                CustomColumnSetting.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        setting = result.scalar_one_or_none()

        if setting is None:
            raise CustomColumnSettingNotFoundError(custom_column_setting_id)

        setting.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    def _to_entity(self, setting: CustomColumnSetting) -> CustomColumnSettingEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return CustomColumnSettingEntity(
            id=setting.id,
            list_id=setting.list_id,
            column_name=setting.column_name,
            display_name=setting.display_name,
            column_config=setting.column_config,
            display_order=setting.display_order,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
            deleted_at=setting.deleted_at,
        )
