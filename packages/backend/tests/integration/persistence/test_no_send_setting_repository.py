"""
送信禁止設定リポジトリの結合テスト

実際のPostgreSQLデータベース（testcontainers）を使用してリポジトリの動作を検証します。
"""
from datetime import date, time

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.no_send_setting_entity import NoSendSettingType
from src.domain.exceptions import NoSendSettingNotFoundError
from src.infrastructure.persistence.models import Organization, List as ListModel
from src.infrastructure.persistence.repositories.no_send_setting_repository import (
    NoSendSettingRepository,
)


@pytest.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """テスト用の組織を作成"""
    from src.infrastructure.persistence.models.organization import OrganizationType

    org = Organization(name="Test Organization", type=OrganizationType.SALES_SUPPORT)
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_list(db_session: AsyncSession, test_organization: Organization) -> ListModel:
    """テスト用のリストを作成"""
    list_model = ListModel(
        organization_id=test_organization.id,
        name="Test List",
        description="Test list for no-send settings",
    )
    db_session.add(list_model)
    await db_session.flush()
    await db_session.refresh(list_model)
    return list_model


@pytest.mark.asyncio
class TestNoSendSettingRepository:
    """送信禁止設定リポジトリのテストクラス"""

    async def test_create_day_of_week_setting(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """曜日ベースの送信禁止設定を作成できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)

        # Act
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="休日送信禁止",
            description="土日の送信を禁止",
            is_enabled=True,
            day_of_week_list=[6, 7],  # 土日
        )

        # Assert
        assert setting.id is not None
        assert setting.list_id == test_list.id
        assert setting.setting_type == NoSendSettingType.DAY_OF_WEEK
        assert setting.name == "休日送信禁止"
        assert setting.day_of_week_list == [6, 7]
        assert setting.is_enabled is True

    async def test_create_time_range_setting(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """時間帯ベースの送信禁止設定を作成できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)

        # Act
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.TIME_RANGE,
            name="夜間送信禁止",
            description="22時から翌朝8時まで送信禁止",
            is_enabled=True,
            time_start=time(22, 0, 0),
            time_end=time(8, 0, 0),
        )

        # Assert
        assert setting.id is not None
        assert setting.list_id == test_list.id
        assert setting.setting_type == NoSendSettingType.TIME_RANGE
        assert setting.name == "夜間送信禁止"
        assert setting.time_start == time(22, 0, 0)
        assert setting.time_end == time(8, 0, 0)
        assert setting.is_enabled is True

    async def test_create_specific_date_setting(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """特定日付の送信禁止設定を作成できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)

        # Act
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.SPECIFIC_DATE,
            name="元旦送信禁止",
            description="元旦の送信を禁止",
            is_enabled=True,
            specific_date=date(2025, 1, 1),
        )

        # Assert
        assert setting.id is not None
        assert setting.list_id == test_list.id
        assert setting.setting_type == NoSendSettingType.SPECIFIC_DATE
        assert setting.name == "元旦送信禁止"
        assert setting.specific_date == date(2025, 1, 1)
        assert setting.is_enabled is True

    async def test_create_date_range_setting(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """日付範囲の送信禁止設定を作成できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)

        # Act
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.SPECIFIC_DATE,
            name="年末年始送信禁止",
            description="年末年始の送信を禁止",
            is_enabled=True,
            date_range_start=date(2025, 12, 29),
            date_range_end=date(2026, 1, 3),
        )

        # Assert
        assert setting.id is not None
        assert setting.list_id == test_list.id
        assert setting.setting_type == NoSendSettingType.SPECIFIC_DATE
        assert setting.name == "年末年始送信禁止"
        assert setting.date_range_start == date(2025, 12, 29)
        assert setting.date_range_end == date(2026, 1, 3)
        assert setting.is_enabled is True

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """IDで送信禁止設定を検索できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        created_setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Test Setting",
            day_of_week_list=[1, 2, 3],
        )

        # Act
        found_setting = await repo.find_by_id(
            no_send_setting_id=created_setting.id,
            requesting_organization_id=test_organization.id,
        )

        # Assert
        assert found_setting is not None
        assert found_setting.id == created_setting.id
        assert found_setting.name == "Test Setting"

    async def test_find_by_id_with_wrong_organization_returns_none(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """異なる組織IDで検索した場合Noneが返ることを確認（IDOR対策）"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        created_setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Test Setting",
            day_of_week_list=[1],
        )

        # Act
        found_setting = await repo.find_by_id(
            no_send_setting_id=created_setting.id,
            requesting_organization_id=99999,  # 存在しない組織ID
        )

        # Assert
        assert found_setting is None

    async def test_list_by_list_id(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """リストIDで送信禁止設定一覧を取得できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Setting 1",
            day_of_week_list=[6, 7],
        )
        await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.TIME_RANGE,
            name="Setting 2",
            time_start=time(22, 0, 0),
            time_end=time(8, 0, 0),
        )

        # Act
        settings = await repo.list_by_list_id(
            list_id=test_list.id,
            requesting_organization_id=test_organization.id,
        )

        # Assert
        assert len(settings) == 2
        assert settings[0].name in ["Setting 1", "Setting 2"]
        assert settings[1].name in ["Setting 1", "Setting 2"]

    async def test_list_by_list_id_exclude_disabled(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """無効な設定が除外されることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Enabled Setting",
            is_enabled=True,
            day_of_week_list=[6],
        )
        await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Disabled Setting",
            is_enabled=False,
            day_of_week_list=[7],
        )

        # Act
        settings = await repo.list_by_list_id(
            list_id=test_list.id,
            requesting_organization_id=test_organization.id,
            include_disabled=False,
        )

        # Assert
        assert len(settings) == 1
        assert settings[0].name == "Enabled Setting"

    async def test_update_setting(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """送信禁止設定を更新できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Original Name",
            day_of_week_list=[6],
        )

        # Act
        setting.name = "Updated Name"
        setting.is_enabled = False
        updated_setting = await repo.update(
            no_send_setting_entity=setting,
            requesting_organization_id=test_organization.id,
        )

        # Assert
        assert updated_setting.id == setting.id
        assert updated_setting.name == "Updated Name"
        assert updated_setting.is_enabled is False

    async def test_update_with_wrong_organization_raises_error(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """異なる組織IDで更新しようとした場合エラーが発生することを確認（IDOR対策）"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Test Setting",
            day_of_week_list=[1],
        )

        # Act & Assert
        setting.name = "Updated Name"
        with pytest.raises(NoSendSettingNotFoundError):
            await repo.update(
                no_send_setting_entity=setting,
                requesting_organization_id=99999,  # 存在しない組織ID
            )

    async def test_soft_delete(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """送信禁止設定を論理削除できることを確認"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Test Setting",
            day_of_week_list=[1],
        )

        # Act
        await repo.soft_delete(
            no_send_setting_id=setting.id,
            requesting_organization_id=test_organization.id,
        )

        # Assert
        found_setting = await repo.find_by_id(
            no_send_setting_id=setting.id,
            requesting_organization_id=test_organization.id,
        )
        assert found_setting is None  # 論理削除されているため取得できない

    async def test_soft_delete_with_wrong_organization_raises_error(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_list: ListModel,
    ):
        """異なる組織IDで削除しようとした場合エラーが発生することを確認（IDOR対策）"""
        # Arrange
        repo = NoSendSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            setting_type=NoSendSettingType.DAY_OF_WEEK,
            name="Test Setting",
            day_of_week_list=[1],
        )

        # Act & Assert
        with pytest.raises(NoSendSettingNotFoundError):
            await repo.soft_delete(
                no_send_setting_id=setting.id,
                requesting_organization_id=99999,  # 存在しない組織ID
            )
