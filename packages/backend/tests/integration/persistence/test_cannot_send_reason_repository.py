"""
送信不可理由リポジトリの結合テスト

実際のデータベースを使用してCannotSendReasonRepositoryの動作を検証します。
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import CannotSendReasonNotFoundError
from src.infrastructure.persistence.repositories.cannot_send_reason_repository import CannotSendReasonRepository


class TestCannotSendReasonRepositoryCreate:
    """送信不可理由作成のテスト"""

    async def test_create_reason_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：送信不可理由を作成できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # Act
        reason = await repo.create(
            reason_code="FORM_NOT_FOUND",
            reason_name="フォームが見つからない",
            description="Webページにフォームが存在しない場合",
            is_active=True,
        )

        # Assert
        assert reason.id > 0
        assert reason.reason_code == "FORM_NOT_FOUND"
        assert reason.reason_name == "フォームが見つからない"
        assert reason.description == "Webページにフォームが存在しない場合"
        assert reason.is_active is True

    async def test_create_reason_minimal(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：必須項目のみで送信不可理由を作成できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # Act
        reason = await repo.create(
            reason_code="CAPTCHA_REQUIRED",
            reason_name="CAPTCHA認証が必要",
        )

        # Assert
        assert reason.id > 0
        assert reason.reason_code == "CAPTCHA_REQUIRED"
        assert reason.reason_name == "CAPTCHA認証が必要"
        assert reason.description is None
        assert reason.is_active is True


class TestCannotSendReasonRepositoryFind:
    """送信不可理由検索のテスト"""

    async def test_find_by_id_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：IDで送信不可理由を検索できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        created = await repo.create(
            reason_code="INVALID_EMAIL",
            reason_name="メールアドレスが無効",
        )

        # Act
        reason = await repo.find_by_id(created.id)

        # Assert
        assert reason is not None
        assert reason.id == created.id
        assert reason.reason_code == "INVALID_EMAIL"
        assert reason.reason_name == "メールアドレスが無効"

    async def test_find_by_id_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：存在しないIDはNoneを返す"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # Act
        reason = await repo.find_by_id(999999)

        # Assert
        assert reason is None

    async def test_find_by_reason_code_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：理由コードで送信不可理由を検索できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        await repo.create(
            reason_code="NETWORK_ERROR",
            reason_name="ネットワークエラー",
        )

        # Act
        reason = await repo.find_by_reason_code("NETWORK_ERROR")

        # Assert
        assert reason is not None
        assert reason.reason_code == "NETWORK_ERROR"
        assert reason.reason_name == "ネットワークエラー"

    async def test_find_by_reason_code_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：存在しない理由コードはNoneを返す"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # Act
        reason = await repo.find_by_reason_code("NON_EXISTENT_CODE")

        # Assert
        assert reason is None

    async def test_list_all_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：送信不可理由の一覧を取得できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # 3つの理由を作成
        await repo.create(
            reason_code="REASON_1",
            reason_name="理由1",
        )
        await repo.create(
            reason_code="REASON_2",
            reason_name="理由2",
        )
        await repo.create(
            reason_code="REASON_3",
            reason_name="理由3",
        )

        # Act
        reason_list = await repo.list_all()

        # Assert
        assert len(reason_list) >= 3
        reason_codes = [r.reason_code for r in reason_list]
        assert "REASON_1" in reason_codes
        assert "REASON_2" in reason_codes
        assert "REASON_3" in reason_codes

    async def test_list_all_with_active_filter(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：有効な理由のみをフィルタリングできる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # 有効な理由と無効な理由を作成
        active_reason = await repo.create(
            reason_code="ACTIVE_REASON",
            reason_name="有効な理由",
            is_active=True,
        )
        inactive_reason = await repo.create(
            reason_code="INACTIVE_REASON",
            reason_name="無効な理由",
            is_active=False,
        )

        # Act
        active_only = await repo.list_all(is_active_only=True)
        all_reasons = await repo.list_all(is_active_only=False)

        # Assert
        active_codes = [r.reason_code for r in active_only]
        all_codes = [r.reason_code for r in all_reasons]

        assert "ACTIVE_REASON" in active_codes
        assert "INACTIVE_REASON" not in active_codes
        assert "ACTIVE_REASON" in all_codes
        assert "INACTIVE_REASON" in all_codes

    async def test_list_all_pagination(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：ページネーションが機能する"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # 5つの理由を作成
        for i in range(5):
            await repo.create(
                reason_code=f"PAGE_TEST_{i}",
                reason_name=f"ページテスト{i}",
            )

        # Act
        first_page = await repo.list_all(skip=0, limit=2)
        second_page = await repo.list_all(skip=2, limit=2)

        # Assert
        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0].id != second_page[0].id

    async def test_count_all_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：送信不可理由の総件数を取得できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # 既存データをカウント
        initial_count = await repo.count_all(is_active_only=False)

        # 2つの理由を作成
        await repo.create(
            reason_code="COUNT_TEST_1",
            reason_name="カウントテスト1",
        )
        await repo.create(
            reason_code="COUNT_TEST_2",
            reason_name="カウントテスト2",
        )

        # Act
        count = await repo.count_all(is_active_only=False)

        # Assert
        assert count == initial_count + 2

    async def test_count_all_with_active_filter(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：有効な理由のみをカウントできる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # 有効な理由と無効な理由を作成
        await repo.create(
            reason_code="COUNT_ACTIVE",
            reason_name="カウント有効",
            is_active=True,
        )
        await repo.create(
            reason_code="COUNT_INACTIVE",
            reason_name="カウント無効",
            is_active=False,
        )

        # Act
        active_count = await repo.count_all(is_active_only=True)
        all_count = await repo.count_all(is_active_only=False)

        # Assert
        assert all_count > active_count


class TestCannotSendReasonRepositoryUpdate:
    """送信不可理由更新のテスト"""

    async def test_update_reason_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：送信不可理由を更新できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        reason = await repo.create(
            reason_code="UPDATE_TEST",
            reason_name="更新テスト",
            is_active=True,
        )

        # Act
        reason.reason_name = "更新後のテスト"
        reason.description = "説明を追加"
        reason.is_active = False
        updated = await repo.update(reason)

        # Assert
        assert updated.id == reason.id
        assert updated.reason_name == "更新後のテスト"
        assert updated.description == "説明を追加"
        assert updated.is_active is False

    async def test_update_reason_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """異常系：存在しない送信不可理由の更新でエラー"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity

        fake_entity = CannotSendReasonEntity(
            id=999999,
            reason_code="FAKE",
            reason_name="偽の理由",
        )

        # Act & Assert
        with pytest.raises(CannotSendReasonNotFoundError):
            await repo.update(fake_entity)


class TestCannotSendReasonRepositorySoftDelete:
    """送信不可理由論理削除のテスト"""

    async def test_soft_delete_success(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：送信不可理由を論理削除できる"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        reason = await repo.create(
            reason_code="DELETE_TEST",
            reason_name="削除テスト",
        )

        # Act
        await repo.soft_delete(reason.id)

        # Assert
        deleted = await repo.find_by_id(reason.id)
        assert deleted is None

    async def test_soft_delete_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        """異常系：存在しない送信不可理由の論理削除でエラー"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)

        # Act & Assert
        with pytest.raises(CannotSendReasonNotFoundError):
            await repo.soft_delete(999999)

    async def test_soft_delete_excludes_from_list(
        self,
        db_session: AsyncSession,
    ) -> None:
        """正常系：削除済み理由は一覧に含まれない"""
        # Arrange
        repo = CannotSendReasonRepository(db_session)
        reason = await repo.create(
            reason_code="LIST_DELETE_TEST",
            reason_name="一覧削除テスト",
        )

        # 削除前の件数
        count_before = await repo.count_all()

        # Act
        await repo.soft_delete(reason.id)

        # Assert
        count_after = await repo.count_all()
        assert count_after == count_before - 1

        # include_deleted=Trueで検索すれば含まれる
        count_with_deleted = await repo.count_all(include_deleted=True)
        assert count_with_deleted == count_before
