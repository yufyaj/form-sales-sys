"""
リストリポジトリの結合テスト

実際のデータベースを使用してListRepositoryの動作を検証します。
TDDサイクル：Red - まず失敗するテストを書きます。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import ListNotFoundError
from src.infrastructure.persistence.models import Organization
from src.infrastructure.persistence.models.organization import OrganizationType
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


class TestListRepositoryCreate:
    """リスト作成のテスト"""

    async def test_create_list_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：リストを作成できる"""
        # Arrange
        repo = ListRepository(db_session)

        # Act
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="IT企業リスト",
            description="IT業界の営業先リスト",
        )

        # Assert
        assert list_entity.id > 0
        assert list_entity.organization_id == sales_support_organization.id
        assert list_entity.name == "IT企業リスト"
        assert list_entity.description == "IT業界の営業先リスト"
        assert list_entity.created_at is not None
        assert list_entity.updated_at is not None
        assert list_entity.deleted_at is None

    async def test_create_list_minimal(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：必須項目のみでリストを作成できる"""
        # Arrange
        repo = ListRepository(db_session)

        # Act
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="製造業リスト",
        )

        # Assert
        assert list_entity.id > 0
        assert list_entity.organization_id == sales_support_organization.id
        assert list_entity.name == "製造業リスト"
        assert list_entity.description is None


class TestListRepositoryFind:
    """リスト検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：IDでリストを検索できる"""
        # Arrange
        repo = ListRepository(db_session)
        created = await repo.create(
            organization_id=sales_support_organization.id,
            name="小売業リスト",
            description="小売業界の営業先",
        )

        # Act
        list_entity = await repo.find_by_id(
            created.id, sales_support_organization.id
        )

        # Assert
        assert list_entity is not None
        assert list_entity.id == created.id
        assert list_entity.name == "小売業リスト"
        assert list_entity.description == "小売業界の営業先"

    async def test_find_by_id_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = ListRepository(db_session)

        # Act
        list_entity = await repo.find_by_id(999999, sales_support_organization.id)

        # Assert
        assert list_entity is None

    async def test_find_by_id_different_tenant(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        another_sales_support_organization: Organization,
    ) -> None:
        """セキュリティ：異なるテナントのリストは取得できない（IDOR対策）"""
        # Arrange
        repo = ListRepository(db_session)
        # テナントAのリストを作成
        created = await repo.create(
            organization_id=sales_support_organization.id,
            name="テナントAのリスト",
        )

        # Act - テナントBからテナントAのリストを検索
        list_entity = await repo.find_by_id(
            created.id, another_sales_support_organization.id
        )

        # Assert - 見つからない（IDOR対策）
        assert list_entity is None

    async def test_list_by_organization_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：組織IDでリスト一覧を取得できる"""
        # Arrange
        repo = ListRepository(db_session)

        # 3つのリストを作成
        for i in range(3):
            await repo.create(
                organization_id=sales_support_organization.id,
                name=f"リスト{i+1}",
                description=f"説明{i+1}",
            )

        # Act
        lists = await repo.list_by_organization(sales_support_organization.id)

        # Assert
        assert len(lists) == 3
        assert all(lst.organization_id == sales_support_organization.id for lst in lists)
        assert all(lst.name in ["リスト1", "リスト2", "リスト3"] for lst in lists)

    async def test_list_by_organization_pagination(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：ページネーションが機能する"""
        # Arrange
        repo = ListRepository(db_session)

        # 5つのリストを作成
        for i in range(5):
            await repo.create(
                organization_id=sales_support_organization.id,
                name=f"リスト{i+1}",
            )

        # Act
        lists_page1 = await repo.list_by_organization(
            sales_support_organization.id, skip=0, limit=2
        )
        lists_page2 = await repo.list_by_organization(
            sales_support_organization.id, skip=2, limit=2
        )

        # Assert
        assert len(lists_page1) == 2
        assert len(lists_page2) == 2
        # IDが重複していないことを確認
        ids_page1 = {lst.id for lst in lists_page1}
        ids_page2 = {lst.id for lst in lists_page2}
        assert len(ids_page1.intersection(ids_page2)) == 0

    async def test_list_by_organization_exclude_deleted(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：デフォルトで削除済みリストを除外する"""
        # Arrange
        repo = ListRepository(db_session)
        list1 = await repo.create(
            organization_id=sales_support_organization.id,
            name="通常リスト",
        )
        list2 = await repo.create(
            organization_id=sales_support_organization.id,
            name="削除予定リスト",
        )

        # list2を削除
        await repo.soft_delete(list2.id, sales_support_organization.id)

        # Act
        lists = await repo.list_by_organization(sales_support_organization.id)

        # Assert
        assert len(lists) == 1
        assert lists[0].id == list1.id


class TestListRepositoryUpdate:
    """リスト更新のテスト"""

    async def test_update_list_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：リストを更新できる"""
        # Arrange
        repo = ListRepository(db_session)
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="古いリスト名",
            description="古い説明",
        )

        # Act
        list_entity.name = "新しいリスト名"
        list_entity.description = "新しい説明"
        updated = await repo.update(list_entity, sales_support_organization.id)

        # Assert
        assert updated.id == list_entity.id
        assert updated.name == "新しいリスト名"
        assert updated.description == "新しい説明"

    async def test_update_list_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないリストの更新でエラー"""
        # Arrange
        repo = ListRepository(db_session)
        from src.domain.entities.list_entity import ListEntity

        fake_entity = ListEntity(
            id=999999,
            organization_id=sales_support_organization.id,
            name="存在しないリスト",
        )

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await repo.update(fake_entity, sales_support_organization.id)

    async def test_update_list_different_tenant(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        another_sales_support_organization: Organization,
    ) -> None:
        """セキュリティ：異なるテナントのリストは更新できない（IDOR対策）"""
        # Arrange
        repo = ListRepository(db_session)
        # テナントAのリストを作成
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="テナントAのリスト",
        )

        # Act & Assert - テナントBからテナントAのリストを更新しようとする
        list_entity.name = "不正な更新"
        with pytest.raises(ListNotFoundError):
            await repo.update(list_entity, another_sales_support_organization.id)


class TestListRepositorySoftDelete:
    """リスト論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
    ) -> None:
        """正常系：リストを論理削除できる"""
        # Arrange
        repo = ListRepository(db_session)
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="削除予定リスト",
        )

        # Act
        await repo.soft_delete(list_entity.id, sales_support_organization.id)

        # Assert
        deleted = await repo.find_by_id(list_entity.id, sales_support_organization.id)
        assert deleted is None

        # include_deleted=Trueで取得できることを確認
        all_lists = await repo.list_by_organization(
            sales_support_organization.id, include_deleted=True
        )
        assert len(all_lists) == 1
        assert all_lists[0].deleted_at is not None

    async def test_soft_delete_not_found(
        self, db_session: AsyncSession, sales_support_organization: Organization
    ) -> None:
        """異常系：存在しないリストの論理削除でエラー"""
        # Arrange
        repo = ListRepository(db_session)

        # Act & Assert
        with pytest.raises(ListNotFoundError):
            await repo.soft_delete(999999, sales_support_organization.id)

    async def test_soft_delete_different_tenant(
        self,
        db_session: AsyncSession,
        sales_support_organization: Organization,
        another_sales_support_organization: Organization,
    ) -> None:
        """セキュリティ：異なるテナントのリストは削除できない（IDOR対策）"""
        # Arrange
        repo = ListRepository(db_session)
        # テナントAのリストを作成
        list_entity = await repo.create(
            organization_id=sales_support_organization.id,
            name="テナントAのリスト",
        )

        # Act & Assert - テナントBからテナントAのリストを削除しようとする
        with pytest.raises(ListNotFoundError):
            await repo.soft_delete(list_entity.id, another_sales_support_organization.id)
