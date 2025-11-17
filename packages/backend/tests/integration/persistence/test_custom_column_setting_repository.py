"""
カスタムカラム設定リポジトリの結合テスト

実際のデータベースを使用してCustomColumnSettingRepositoryの動作を検証します。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import CustomColumnSettingNotFoundError
from src.infrastructure.persistence.models import List, Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.custom_column_setting_repository import (
    CustomColumnSettingRepository,
)
from src.infrastructure.persistence.repositories.list_repository import ListRepository


@pytest.fixture
async def sales_support_organization(db_session: AsyncSession) -> Organization:
    """テスト用営業支援会社組織を作成"""
    org = Organization(
        name="テスト営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="sales@example.com",
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest.fixture
async def test_list(
    db_session: AsyncSession, sales_support_organization: Organization
) -> List:
    """テスト用リストを作成"""
    repo = ListRepository(db_session)
    list_entity = await repo.create(
        organization_id=sales_support_organization.id,
        name="IT企業リスト",
    )
    from sqlalchemy import select

    stmt = select(List).where(List.id == list_entity.id)
    result = await db_session.execute(stmt)
    return result.scalar_one()


class TestCustomColumnSettingRepositoryCreate:
    """カスタムカラム設定作成のテスト"""

    async def test_create_custom_column_setting_success(
        self,
        db_session: AsyncSession,
        test_list: List,
    ) -> None:
        """正常系：カスタムカラム設定を作成できる"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)
        column_config = {
            "type": "string",
            "validation": {"required": True, "max_length": 255},
        }

        # Act
        setting = await repo.create(
            list_id=test_list.id,
            column_name="company_email",
            display_name="企業メールアドレス",
            column_config=column_config,
            display_order=1,
        )

        # Assert
        assert setting.id > 0
        assert setting.list_id == test_list.id
        assert setting.column_name == "company_email"
        assert setting.display_name == "企業メールアドレス"
        assert setting.column_config == column_config
        assert setting.display_order == 1


class TestCustomColumnSettingRepositoryFind:
    """カスタムカラム設定検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：IDでカスタムカラム設定を検索できる"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)
        created = await repo.create(
            list_id=test_list.id,
            column_name="phone",
            display_name="電話番号",
            column_config={"type": "string"},
            display_order=1,
        )

        # Act
        setting = await repo.find_by_id(
            created.id, sales_support_organization.id
        )

        # Assert
        assert setting is not None
        assert setting.id == created.id
        assert setting.column_name == "phone"

    async def test_list_by_list_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リストIDでカスタムカラム設定一覧を取得できる（表示順序でソート）"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)

        # 3つのカラム設定を作成（display_orderを逆順に）
        await repo.create(
            list_id=test_list.id,
            column_name="col3",
            display_name="カラム3",
            column_config={"type": "string"},
            display_order=3,
        )
        await repo.create(
            list_id=test_list.id,
            column_name="col1",
            display_name="カラム1",
            column_config={"type": "string"},
            display_order=1,
        )
        await repo.create(
            list_id=test_list.id,
            column_name="col2",
            display_name="カラム2",
            column_config={"type": "string"},
            display_order=2,
        )

        # Act
        settings = await repo.list_by_list_id(
            test_list.id, sales_support_organization.id
        )

        # Assert
        assert len(settings) == 3
        # display_orderでソートされていることを確認
        assert settings[0].display_order == 1
        assert settings[1].display_order == 2
        assert settings[2].display_order == 3


class TestCustomColumnSettingRepositoryUpdate:
    """カスタムカラム設定更新のテスト"""

    async def test_update_custom_column_setting_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：カスタムカラム設定を更新できる"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            column_name="email",
            display_name="古い表示名",
            column_config={"type": "string"},
            display_order=1,
        )

        # Act
        setting.display_name = "新しい表示名"
        setting.column_config = {"type": "email", "validation": {"required": True}}
        updated = await repo.update(setting, sales_support_organization.id)

        # Assert
        assert updated.id == setting.id
        assert updated.display_name == "新しい表示名"
        assert updated.column_config["type"] == "email"

    async def test_update_custom_column_setting_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないカスタムカラム設定の更新でエラー"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)
        from src.domain.entities.custom_column_setting_entity import (
            CustomColumnSettingEntity,
        )

        fake_entity = CustomColumnSettingEntity(
            id=999999,
            list_id=1,
            column_name="fake",
            display_name="存在しない",
            column_config={},
            display_order=1,
        )

        # Act & Assert
        with pytest.raises(CustomColumnSettingNotFoundError):
            await repo.update(fake_entity, sales_support_organization.id)


class TestCustomColumnSettingRepositorySoftDelete:
    """カスタムカラム設定論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：カスタムカラム設定を論理削除できる"""
        # Arrange
        repo = CustomColumnSettingRepository(db_session)
        setting = await repo.create(
            list_id=test_list.id,
            column_name="temp",
            display_name="削除予定",
            column_config={"type": "string"},
            display_order=1,
        )

        # Act
        await repo.soft_delete(setting.id, sales_support_organization.id)

        # Assert
        deleted = await repo.find_by_id(setting.id, sales_support_organization.id)
        assert deleted is None
