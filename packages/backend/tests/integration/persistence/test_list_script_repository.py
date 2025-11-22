"""
ListScriptモデルの統合テスト

実際のPostgreSQLコンテナを使用してスクリプトモデルのCRUD操作をテストします。
TDDサイクルに従って、まずテストを書いてから実装を確認します。
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import (
    List,
    ListScript,
    Organization,
    OrganizationType,
)


class TestListScriptModel:
    """スクリプトモデルのテスト"""

    @pytest.mark.asyncio
    async def test_create_list_script(self, db_session: AsyncSession) -> None:
        """スクリプトを作成できること"""
        # Arrange
        org = Organization(
            name="テスト営業支援会社",
            type=OrganizationType.SALES_SUPPORT,
            email="test@example.com",
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(
            organization_id=org.id,
            name="テストリスト",
            description="テスト用のリスト",
        )
        db_session.add(list_obj)
        await db_session.flush()

        script = ListScript(
            list_id=list_obj.id,
            title="初回アプローチ用スクリプト",
            content="お世話になっております。〇〇社の△△と申します。",
        )

        # Act
        db_session.add(script)
        await db_session.flush()
        await db_session.refresh(script)

        # Assert
        assert script.id is not None
        assert script.list_id == list_obj.id
        assert script.title == "初回アプローチ用スクリプト"
        assert script.content == "お世話になっております。〇〇社の△△と申します。"
        assert script.created_at is not None
        assert script.updated_at is not None
        assert script.deleted_at is None
        assert script.is_deleted is False

    @pytest.mark.asyncio
    async def test_list_script_relationship(self, db_session: AsyncSession) -> None:
        """リストとスクリプトのリレーションシップが正しく動作すること"""
        # Arrange
        org = Organization(
            name="リレーションテスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(
            organization_id=org.id,
            name="リレーションテストリスト",
        )
        db_session.add(list_obj)
        await db_session.flush()

        script1 = ListScript(
            list_id=list_obj.id,
            title="スクリプト1",
            content="内容1",
        )
        script2 = ListScript(
            list_id=list_obj.id,
            title="スクリプト2",
            content="内容2",
        )
        db_session.add_all([script1, script2])
        await db_session.flush()

        # Act
        result = await db_session.execute(
            select(List).where(List.id == list_obj.id)
        )
        fetched_list = result.scalar_one()
        await db_session.refresh(fetched_list, ["scripts"])

        # Assert
        assert len(fetched_list.scripts) == 2
        script_titles = {s.title for s in fetched_list.scripts}
        assert "スクリプト1" in script_titles
        assert "スクリプト2" in script_titles

    @pytest.mark.asyncio
    async def test_soft_delete_list_script(self, db_session: AsyncSession) -> None:
        """スクリプトを論理削除できること"""
        # Arrange
        from datetime import datetime, timezone

        org = Organization(
            name="削除テスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(organization_id=org.id, name="削除テストリスト")
        db_session.add(list_obj)
        await db_session.flush()

        script = ListScript(
            list_id=list_obj.id,
            title="削除テストスクリプト",
            content="削除テスト内容",
        )
        db_session.add(script)
        await db_session.flush()

        # Act
        script.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()
        await db_session.refresh(script)

        # Assert
        assert script.deleted_at is not None
        assert script.is_deleted is True

    @pytest.mark.asyncio
    async def test_cascade_delete_on_list_deletion(self, db_session: AsyncSession) -> None:
        """リストが削除されたときにスクリプトもカスケード削除されること"""
        # Arrange
        org = Organization(
            name="カスケード削除テスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(organization_id=org.id, name="カスケード削除テストリスト")
        db_session.add(list_obj)
        await db_session.flush()

        script = ListScript(
            list_id=list_obj.id,
            title="カスケード削除テストスクリプト",
            content="カスケード削除テスト内容",
        )
        db_session.add(script)
        await db_session.flush()
        script_id = script.id

        # Act
        await db_session.delete(list_obj)
        await db_session.flush()

        # Assert
        result = await db_session.execute(
            select(ListScript).where(ListScript.id == script_id)
        )
        deleted_script = result.scalar_one_or_none()
        assert deleted_script is None

    @pytest.mark.asyncio
    async def test_update_list_script(self, db_session: AsyncSession) -> None:
        """スクリプトを更新できること"""
        # Arrange
        org = Organization(
            name="更新テスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(organization_id=org.id, name="更新テストリスト")
        db_session.add(list_obj)
        await db_session.flush()

        script = ListScript(
            list_id=list_obj.id,
            title="元のタイトル",
            content="元の内容",
        )
        db_session.add(script)
        await db_session.flush()

        # Act
        script.title = "更新後のタイトル"
        script.content = "更新後の内容"
        await db_session.flush()
        await db_session.refresh(script)

        # Assert
        assert script.title == "更新後のタイトル"
        assert script.content == "更新後の内容"
        assert script.updated_at is not None

    @pytest.mark.asyncio
    async def test_query_scripts_by_list(self, db_session: AsyncSession) -> None:
        """特定のリストに紐づくスクリプトを取得できること"""
        # Arrange
        org = Organization(
            name="クエリテスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list1 = List(organization_id=org.id, name="リスト1")
        list2 = List(organization_id=org.id, name="リスト2")
        db_session.add_all([list1, list2])
        await db_session.flush()

        script1 = ListScript(list_id=list1.id, title="リスト1のスクリプト", content="内容1")
        script2 = ListScript(list_id=list2.id, title="リスト2のスクリプト", content="内容2")
        db_session.add_all([script1, script2])
        await db_session.flush()

        # Act
        result = await db_session.execute(
            select(ListScript).where(ListScript.list_id == list1.id)
        )
        list1_scripts = result.scalars().all()

        # Assert
        assert len(list1_scripts) == 1
        assert list1_scripts[0].title == "リスト1のスクリプト"

    @pytest.mark.asyncio
    async def test_filter_out_deleted_scripts(self, db_session: AsyncSession) -> None:
        """論理削除されたスクリプトを除外できること"""
        # Arrange
        from datetime import datetime, timezone

        org = Organization(
            name="フィルタテスト組織",
            type=OrganizationType.SALES_SUPPORT,
        )
        db_session.add(org)
        await db_session.flush()

        list_obj = List(organization_id=org.id, name="フィルタテストリスト")
        db_session.add(list_obj)
        await db_session.flush()

        active_script = ListScript(
            list_id=list_obj.id,
            title="有効なスクリプト",
            content="有効な内容",
        )
        deleted_script = ListScript(
            list_id=list_obj.id,
            title="削除されたスクリプト",
            content="削除された内容",
        )
        db_session.add_all([active_script, deleted_script])
        await db_session.flush()

        deleted_script.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        # Act
        result = await db_session.execute(
            select(ListScript)
            .where(ListScript.list_id == list_obj.id)
            .where(ListScript.deleted_at.is_(None))
        )
        active_scripts = result.scalars().all()

        # Assert
        assert len(active_scripts) == 1
        assert active_scripts[0].title == "有効なスクリプト"

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, db_session: AsyncSession) -> None:
        """異なる組織のスクリプトにアクセスできないこと（マルチテナント分離）"""
        # Arrange: 2つの異なる組織を作成
        org1 = Organization(
            name="組織A",
            type=OrganizationType.SALES_SUPPORT,
            email="orga@example.com",
        )
        org2 = Organization(
            name="組織B",
            type=OrganizationType.SALES_SUPPORT,
            email="orgb@example.com",
        )
        db_session.add_all([org1, org2])
        await db_session.flush()

        list1 = List(organization_id=org1.id, name="組織Aのリスト")
        list2 = List(organization_id=org2.id, name="組織Bのリスト")
        db_session.add_all([list1, list2])
        await db_session.flush()

        script1 = ListScript(
            list_id=list1.id, title="組織Aのスクリプト", content="内容A"
        )
        script2 = ListScript(
            list_id=list2.id, title="組織Bのスクリプト", content="内容B"
        )
        db_session.add_all([script1, script2])
        await db_session.flush()

        # Act: 組織Aの視点でクエリ（リポジトリレイヤーで実装する想定）
        result = await db_session.execute(
            select(ListScript).join(List).where(List.organization_id == org1.id)
        )
        org1_scripts = result.scalars().all()

        # Assert: 組織Aのスクリプトのみ取得できること
        assert len(org1_scripts) == 1
        assert org1_scripts[0].title == "組織Aのスクリプト"

        # Act: 組織Bの視点でクエリ
        result = await db_session.execute(
            select(ListScript).join(List).where(List.organization_id == org2.id)
        )
        org2_scripts = result.scalars().all()

        # Assert: 組織Bのスクリプトのみ取得できること
        assert len(org2_scripts) == 1
        assert org2_scripts[0].title == "組織Bのスクリプト"
