"""
送信不可理由リポジトリの実装

ICannotSendReasonRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity
from src.domain.exceptions import CannotSendReasonNotFoundError
from src.domain.interfaces.cannot_send_reason_repository import ICannotSendReasonRepository
from src.infrastructure.persistence.models.cannot_send_reason import CannotSendReason

# セキュリティログ用のロガー
logger = logging.getLogger(__name__)


class CannotSendReasonRepository(ICannotSendReasonRepository):
    """
    送信不可理由リポジトリの実装

    SQLAlchemyを使用して送信不可理由マスターデータの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        reason_code: str,
        reason_name: str,
        description: str | None = None,
        is_active: bool = True,
    ) -> CannotSendReasonEntity:
        """送信不可理由を作成"""
        reason = CannotSendReason(
            reason_code=reason_code,
            reason_name=reason_name,
            description=description,
            is_active=is_active,
        )

        self._session.add(reason)
        await self._session.flush()
        await self._session.refresh(reason)

        logger.info(
            "Cannot send reason created successfully",
            extra={
                "event_type": "cannot_send_reason_created",
                "reason_id": reason.id,
                "reason_code": reason_code,
                "reason_name": reason_name,
                "is_active": is_active,
            },
        )

        return self._to_entity(reason)

    async def find_by_id(
        self,
        reason_id: int,
    ) -> CannotSendReasonEntity | None:
        """IDで送信不可理由を検索"""
        stmt = select(CannotSendReason).where(
            CannotSendReason.id == reason_id,
            CannotSendReason.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        reason = result.scalar_one_or_none()

        return self._to_entity(reason) if reason else None

    async def find_by_reason_code(
        self,
        reason_code: str,
    ) -> CannotSendReasonEntity | None:
        """理由コードで送信不可理由を検索"""
        stmt = select(CannotSendReason).where(
            CannotSendReason.reason_code == reason_code,
            CannotSendReason.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        reason = result.scalar_one_or_none()

        return self._to_entity(reason) if reason else None

    async def list_all(
        self,
        is_active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[CannotSendReasonEntity]:
        """送信不可理由の一覧を取得"""
        conditions = []

        if is_active_only:
            conditions.append(CannotSendReason.is_active == True)
        if not include_deleted:
            conditions.append(CannotSendReason.deleted_at.is_(None))

        stmt = (
            select(CannotSendReason)
            .where(and_(*conditions)) if conditions else select(CannotSendReason)
        )
        stmt = (
            stmt
            .offset(skip)
            .limit(limit)
            .order_by(CannotSendReason.reason_code)
        )

        result = await self._session.execute(stmt)
        reason_list = result.scalars().all()

        return [self._to_entity(r) for r in reason_list]

    async def count_all(
        self,
        is_active_only: bool = True,
        include_deleted: bool = False,
    ) -> int:
        """送信不可理由の総件数を取得"""
        conditions = []

        if is_active_only:
            conditions.append(CannotSendReason.is_active == True)
        if not include_deleted:
            conditions.append(CannotSendReason.deleted_at.is_(None))

        stmt = (
            select(func.count())
            .select_from(CannotSendReason)
            .where(and_(*conditions)) if conditions else select(func.count()).select_from(CannotSendReason)
        )

        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

    async def update(
        self,
        reason: CannotSendReasonEntity,
    ) -> CannotSendReasonEntity:
        """送信不可理由を更新"""
        stmt = select(CannotSendReason).where(
            CannotSendReason.id == reason.id,
            CannotSendReason.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        db_reason = result.scalar_one_or_none()

        if db_reason is None:
            raise CannotSendReasonNotFoundError(reason.id)

        # 更新前の値を保存（変更検知用）
        old_reason_code = db_reason.reason_code
        old_reason_name = db_reason.reason_name
        old_is_active = db_reason.is_active
        old_description = db_reason.description

        # エンティティの値でモデルを更新
        db_reason.reason_code = reason.reason_code
        db_reason.reason_name = reason.reason_name
        db_reason.description = reason.description
        db_reason.is_active = reason.is_active

        await self._session.flush()
        await self._session.refresh(db_reason)

        # 変更されたフィールドのみをログに記録（機密情報保護）
        changed_fields = []
        if old_reason_code != reason.reason_code:
            changed_fields.append("reason_code")
        if old_reason_name != reason.reason_name:
            changed_fields.append("reason_name")
        if old_is_active != reason.is_active:
            changed_fields.append("is_active")

        logger.info(
            "Cannot send reason updated successfully",
            extra={
                "event_type": "cannot_send_reason_updated",
                "reason_id": reason.id,
                "changed_fields": changed_fields,
                # descriptionは機密情報を含む可能性があるため、変更の有無のみ記録
                "description_changed": old_description != reason.description,
            },
        )

        return self._to_entity(db_reason)

    async def soft_delete(
        self,
        reason_id: int,
    ) -> None:
        """送信不可理由を論理削除（ソフトデリート）"""
        stmt = select(CannotSendReason).where(
            CannotSendReason.id == reason_id,
            CannotSendReason.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        reason = result.scalar_one_or_none()

        if reason is None:
            raise CannotSendReasonNotFoundError(reason_id)

        reason.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

        logger.info(
            "Cannot send reason soft deleted successfully",
            extra={
                "event_type": "cannot_send_reason_deleted",
                "reason_id": reason_id,
                "reason_code": reason.reason_code,
            },
        )

    def _to_entity(self, reason: CannotSendReason) -> CannotSendReasonEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return CannotSendReasonEntity(
            id=reason.id,
            reason_code=reason.reason_code,
            reason_name=reason.reason_name,
            description=reason.description,
            is_active=reason.is_active,
            created_at=reason.created_at,
            updated_at=reason.updated_at,
            deleted_at=reason.deleted_at,
        )
