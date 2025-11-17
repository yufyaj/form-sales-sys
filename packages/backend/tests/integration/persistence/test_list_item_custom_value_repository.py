"""
リスト項目カスタム値リポジトリの結合テスト

実際のデータベースを使用してListItemCustomValueRepositoryの動作を検証します。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ListItemCustomValueNotFoundError
from src.infrastructure.persistence.models import List, Organization
from src.infrastructure.persistence.models.organization import OrganizationType
from src.infrastructure.persistence.repositories.custom_column_setting_repository import (
    CustomColumnSettingRepository,
)
from src.infrastructure.persistence.repositories.list_item_custom_value_repository import (
    ListItemCustomValueRepository,
)
from src.infrastructure.persistence.repositories.list_item_repository import (
    ListItemRepository,
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


class TestListItemCustomValueRepositoryCreate:
    """リスト項目カスタム値作成のテスト"""

    async def test_create_custom_value_success(
        self,
        db_session: AsyncSession,
        test_list: List,
    ) -> None:
        """正常系：リスト項目カスタム値を作成できる"""
        # Arrange
        # リスト項目を作成
        item_repo = ListItemRepository(db_session)
        item = await item_repo.create(
            list_id=test_list.id,
            title="株式会社テスト",
        )

        # カスタムカラム設定を作成
        setting_repo = CustomColumnSettingRepository(db_session)
        setting = await setting_repo.create(
            list_id=test_list.id,
            column_name="email",
            display_name="メールアドレス",
            column_config={"type": "email"},
            display_order=1,
        )

        # Act
        value_repo = ListItemCustomValueRepository(db_session)
        custom_value = await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting.id,
            value={"email": "test@example.com"},
        )

        # Assert
        assert custom_value.id > 0
        assert custom_value.list_item_id == item.id
        assert custom_value.custom_column_setting_id == setting.id
        assert custom_value.value == {"email": "test@example.com"}


class TestListItemCustomValueRepositoryFind:
    """リスト項目カスタム値検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：IDでリスト項目カスタム値を検索できる"""
        # Arrange
        item_repo = ListItemRepository(db_session)
        item = await item_repo.create(list_id=test_list.id, title="企業A")

        setting_repo = CustomColumnSettingRepository(db_session)
        setting = await setting_repo.create(
            list_id=test_list.id,
            column_name="phone",
            display_name="電話番号",
            column_config={"type": "string"},
            display_order=1,
        )

        value_repo = ListItemCustomValueRepository(db_session)
        created = await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting.id,
            value={"phone": "03-1234-5678"},
        )

        # Act
        custom_value = await value_repo.find_by_id(
            created.id, sales_support_organization.id
        )

        # Assert
        assert custom_value is not None
        assert custom_value.id == created.id
        assert custom_value.value == {"phone": "03-1234-5678"}

    async def test_list_by_list_item_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リスト項目IDでカスタム値一覧を取得できる"""
        # Arrange
        item_repo = ListItemRepository(db_session)
        item = await item_repo.create(list_id=test_list.id, title="企業A")

        setting_repo = CustomColumnSettingRepository(db_session)
        setting1 = await setting_repo.create(
            list_id=test_list.id,
            column_name="email",
            display_name="メール",
            column_config={"type": "email"},
            display_order=1,
        )
        setting2 = await setting_repo.create(
            list_id=test_list.id,
            column_name="phone",
            display_name="電話",
            column_config={"type": "string"},
            display_order=2,
        )

        value_repo = ListItemCustomValueRepository(db_session)
        await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting1.id,
            value={"email": "test@example.com"},
        )
        await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting2.id,
            value={"phone": "03-1234-5678"},
        )

        # Act
        values = await value_repo.list_by_list_item_id(
            item.id, sales_support_organization.id
        )

        # Assert
        assert len(values) == 2
        assert all(v.list_item_id == item.id for v in values)


class TestListItemCustomValueRepositoryUpdate:
    """リスト項目カスタム値更新のテスト"""

    async def test_update_custom_value_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リスト項目カスタム値を更新できる"""
        # Arrange
        item_repo = ListItemRepository(db_session)
        item = await item_repo.create(list_id=test_list.id, title="企業A")

        setting_repo = CustomColumnSettingRepository(db_session)
        setting = await setting_repo.create(
            list_id=test_list.id,
            column_name="email",
            display_name="メール",
            column_config={"type": "email"},
            display_order=1,
        )

        value_repo = ListItemCustomValueRepository(db_session)
        custom_value = await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting.id,
            value={"email": "old@example.com"},
        )

        # Act
        custom_value.value = {"email": "new@example.com"}
        updated = await value_repo.update(custom_value, sales_support_organization.id)

        # Assert
        assert updated.id == custom_value.id
        assert updated.value == {"email": "new@example.com"}

    async def test_update_custom_value_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないカスタム値の更新でエラー"""
        # Arrange
        value_repo = ListItemCustomValueRepository(db_session)
        from src.domain.entities.list_item_custom_value_entity import (
            ListItemCustomValueEntity,
        )

        fake_entity = ListItemCustomValueEntity(
            id=999999,
            list_item_id=1,
            custom_column_setting_id=1,
            value={},
        )

        # Act & Assert
        with pytest.raises(ListItemCustomValueNotFoundError):
            await value_repo.update(fake_entity, sales_support_organization.id)


class TestListItemCustomValueRepositorySoftDelete:
    """リスト項目カスタム値論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リスト項目カスタム値を論理削除できる"""
        # Arrange
        item_repo = ListItemRepository(db_session)
        item = await item_repo.create(list_id=test_list.id, title="企業A")

        setting_repo = CustomColumnSettingRepository(db_session)
        setting = await setting_repo.create(
            list_id=test_list.id,
            column_name="temp",
            display_name="削除予定",
            column_config={"type": "string"},
            display_order=1,
        )

        value_repo = ListItemCustomValueRepository(db_session)
        custom_value = await value_repo.create(
            list_item_id=item.id,
            custom_column_setting_id=setting.id,
            value={"temp": "value"},
        )

        # Act
        await value_repo.soft_delete(custom_value.id, sales_support_organization.id)

        # Assert
        deleted = await value_repo.find_by_id(
            custom_value.id, sales_support_organization.id
        )
        assert deleted is None
