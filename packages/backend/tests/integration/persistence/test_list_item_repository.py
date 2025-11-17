"""
リスト項目リポジトリの結合テスト

実際のデータベースを使用してListItemRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ListItemNotFoundError
from src.infrastructure.persistence.models import List, Organization
from src.infrastructure.persistence.models.organization import OrganizationType
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
async def another_sales_support_organization(db_session: AsyncSession) -> Organization:
    """テスト用の別の営業支援会社組織を作成（テナント分離テスト用）"""
    org = Organization(
        name="別の営業支援会社",
        type=OrganizationType.SALES_SUPPORT,
        email="another@example.com",
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
        description="テスト用リスト",
    )
    # DBモデルを取得して返す
    from sqlalchemy import select

    stmt = select(List).where(List.id == list_entity.id)
    result = await db_session.execute(stmt)
    return result.scalar_one()


class TestListItemRepositoryCreate:
    """リスト項目作成のテスト"""

    async def test_create_list_item_success(
        self,
        db_session: AsyncSession,
        test_list: List,
    ) -> None:
        """正常系：リスト項目を作成できる"""
        # Arrange
        repo = ListItemRepository(db_session)

        # Act
        item = await repo.create(
            list_id=test_list.id,
            title="株式会社テスト",
            status="pending",
        )

        # Assert
        assert item.id > 0
        assert item.list_id == test_list.id
        assert item.title == "株式会社テスト"
        assert item.status == "pending"
        assert item.created_at is not None
        assert item.updated_at is not None
        assert item.deleted_at is None

    async def test_create_list_item_default_status(
        self,
        db_session: AsyncSession,
        test_list: List,
    ) -> None:
        """正常系：ステータスのデフォルト値がpending"""
        # Arrange
        repo = ListItemRepository(db_session)

        # Act
        item = await repo.create(
            list_id=test_list.id,
            title="株式会社サンプル",
        )

        # Assert
        assert item.status == "pending"


class TestListItemRepositoryFind:
    """リスト項目検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：IDでリスト項目を検索できる"""
        # Arrange
        repo = ListItemRepository(db_session)
        created = await repo.create(
            list_id=test_list.id,
            title="株式会社ABC",
            status="contacted",
        )

        # Act
        item = await repo.find_by_id(created.id, sales_support_organization.id)

        # Assert
        assert item is not None
        assert item.id == created.id
        assert item.title == "株式会社ABC"
        assert item.status == "contacted"

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ListItemRepository(db_session)

        # Act
        item = await repo.find_by_id(999999, sales_support_organization.id)

        # Assert
        assert item is None

    async def test_find_by_id_different_tenant(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        another_sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """セキュリティ：異なるテナントのリスト項目は取得できない（IDOR対策）"""
        # Arrange
        repo = ListItemRepository(db_session)
        created = await repo.create(
            list_id=test_list.id,
            title="テナントAの項目",
        )

        # Act - テナントBからテナントAのリスト項目を検索
        item = await repo.find_by_id(created.id, another_sales_support_organization.id)

        # Assert - 見つからない（IDOR対策）
        assert item is None

    async def test_list_by_list_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リストIDでリスト項目一覧を取得できる"""
        # Arrange
        repo = ListItemRepository(db_session)

        # 3つのリスト項目を作成
        for i in range(3):
            await repo.create(
                list_id=test_list.id,
                title=f"企業{i+1}",
                status="pending",
            )

        # Act
        items = await repo.list_by_list_id(
            test_list.id, sales_support_organization.id
        )

        # Assert
        assert len(items) == 3
        assert all(item.list_id == test_list.id for item in items)

    async def test_list_by_list_id_pagination(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：ページネーションが機能する"""
        # Arrange
        repo = ListItemRepository(db_session)

        # 5つのリスト項目を作成
        for i in range(5):
            await repo.create(
                list_id=test_list.id,
                title=f"企業{i+1}",
            )

        # Act
        items_page1 = await repo.list_by_list_id(
            test_list.id, sales_support_organization.id, skip=0, limit=2
        )
        items_page2 = await repo.list_by_list_id(
            test_list.id, sales_support_organization.id, skip=2, limit=2
        )

        # Assert
        assert len(items_page1) == 2
        assert len(items_page2) == 2
        ids_page1 = {item.id for item in items_page1}
        ids_page2 = {item.id for item in items_page2}
        assert len(ids_page1.intersection(ids_page2)) == 0


class TestListItemRepositoryUpdate:
    """リスト項目更新のテスト"""

    async def test_update_list_item_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リスト項目を更新できる"""
        # Arrange
        repo = ListItemRepository(db_session)
        item = await repo.create(
            list_id=test_list.id,
            title="古いタイトル",
            status="pending",
        )

        # Act
        item.title = "新しいタイトル"
        item.status = "contacted"
        updated = await repo.update(item, sales_support_organization.id)

        # Assert
        assert updated.id == item.id
        assert updated.title == "新しいタイトル"
        assert updated.status == "contacted"

    async def test_update_list_item_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないリスト項目の更新でエラー"""
        # Arrange
        repo = ListItemRepository(db_session)
        from src.domain.entities.list_item_entity import ListItemEntity

        fake_entity = ListItemEntity(
            id=999999,
            list_id=1,
            title="存在しない項目",
            status="pending",
        )

        # Act & Assert
        with pytest.raises(ListItemNotFoundError):
            await repo.update(fake_entity, sales_support_organization.id)


class TestListItemRepositorySoftDelete:
    """リスト項目論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        test_list: List,
    ) -> None:
        """正常系：リスト項目を論理削除できる"""
        # Arrange
        repo = ListItemRepository(db_session)
        item = await repo.create(
            list_id=test_list.id,
            title="削除予定項目",
        )

        # Act
        await repo.soft_delete(item.id, sales_support_organization.id)

        # Assert
        deleted = await repo.find_by_id(item.id, sales_support_organization.id)
        assert deleted is None

        # include_deleted=Trueで取得できることを確認
        all_items = await repo.list_by_list_id(
            test_list.id, sales_support_organization.id, include_deleted=True
        )
        assert len(all_items) == 1
        assert all_items[0].deleted_at is not None

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないリスト項目の論理削除でエラー"""
        # Arrange
        repo = ListItemRepository(db_session)

        # Act & Assert
        with pytest.raises(ListItemNotFoundError):
            await repo.soft_delete(999999, sales_support_organization.id)
