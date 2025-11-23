"""
送信不可理由管理ユースケース

送信不可理由マスタデータのCRUD操作とビジネスロジックを実行します。
営業支援会社がカスタマイズ可能なマスタデータです。
"""

import logging
from dataclasses import replace

from src.application.schemas.cannot_send_reason import (
    CannotSendReasonCreateRequest,
    CannotSendReasonUpdateRequest,
)
from src.domain.entities.cannot_send_reason_entity import CannotSendReasonEntity
from src.domain.exceptions import (
    CannotSendReasonNotFoundError,
    DuplicateCannotSendReasonCodeError,
)
from src.domain.interfaces.cannot_send_reason_repository import (
    ICannotSendReasonRepository,
)

logger = logging.getLogger(__name__)


class CannotSendReasonUseCases:
    """送信不可理由管理ユースケースクラス"""

    def __init__(
        self,
        cannot_send_reason_repository: ICannotSendReasonRepository,
    ) -> None:
        """
        Args:
            cannot_send_reason_repository: 送信不可理由リポジトリ
        """
        self._repo = cannot_send_reason_repository

    async def create_reason(
        self,
        request: CannotSendReasonCreateRequest,
    ) -> CannotSendReasonEntity:
        """
        送信不可理由を作成

        Args:
            request: 送信不可理由作成リクエスト

        Returns:
            作成された送信不可理由エンティティ

        Raises:
            DuplicateCannotSendReasonCodeError: 同じ理由コードが既に登録されている場合
        """
        # 理由コードの重複チェック
        existing_reason = await self._repo.find_by_reason_code(
            reason_code=request.reason_code,
        )
        if existing_reason is not None:
            logger.warning(
                "Duplicate cannot send reason code attempt",
                extra={
                    "event": "cannot_send_reason_duplicate",
                    "reason_code": request.reason_code,
                },
            )
            raise DuplicateCannotSendReasonCodeError(request.reason_code)

        # 送信不可理由を作成
        reason = await self._repo.create(
            reason_code=request.reason_code,
            reason_name=request.reason_name,
            description=request.description,
            is_active=request.is_active,
        )

        logger.info(
            "Cannot send reason created successfully",
            extra={
                "event": "cannot_send_reason_created",
                "reason_id": reason.id,
                "reason_code": reason.reason_code,
                "is_active": reason.is_active,
            },
        )

        return reason

    async def get_reason(
        self,
        reason_id: int,
    ) -> CannotSendReasonEntity:
        """
        送信不可理由を取得

        Args:
            reason_id: 送信不可理由ID

        Returns:
            送信不可理由エンティティ

        Raises:
            CannotSendReasonNotFoundError: 送信不可理由が見つからない場合
        """
        reason = await self._repo.find_by_id(reason_id=reason_id)
        if reason is None:
            raise CannotSendReasonNotFoundError(reason_id)

        return reason

    async def list_reasons(
        self,
        is_active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CannotSendReasonEntity], int]:
        """
        送信不可理由の一覧を取得

        Args:
            is_active_only: 有効な理由のみを取得するか
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数

        Returns:
            tuple[list[CannotSendReasonEntity], int]:
                - 送信不可理由エンティティのリスト
                - 総件数
        """
        reasons = await self._repo.list_all(
            is_active_only=is_active_only,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )

        total = await self._repo.count_all(
            is_active_only=is_active_only,
            include_deleted=False,
        )

        return reasons, total

    async def update_reason(
        self,
        reason_id: int,
        request: CannotSendReasonUpdateRequest,
    ) -> CannotSendReasonEntity:
        """
        送信不可理由を更新

        Args:
            reason_id: 送信不可理由ID
            request: 送信不可理由更新リクエスト

        Returns:
            更新された送信不可理由エンティティ

        Raises:
            CannotSendReasonNotFoundError: 送信不可理由が見つからない場合
            DuplicateCannotSendReasonCodeError: 理由コードが他のレコードと重複している場合
        """
        # 更新対象の取得
        reason = await self._repo.find_by_id(reason_id=reason_id)
        if reason is None:
            raise CannotSendReasonNotFoundError(reason_id)

        # 理由コードの重複チェック（コードが変更される場合のみ）
        if request.reason_code is not None and request.reason_code != reason.reason_code:
            existing_reason = await self._repo.find_by_reason_code(
                reason_code=request.reason_code,
            )
            if existing_reason is not None:
                logger.warning(
                    "Duplicate cannot send reason code on update",
                    extra={
                        "event": "cannot_send_reason_duplicate_on_update",
                        "reason_id": reason_id,
                        "reason_code": request.reason_code,
                    },
                )
                raise DuplicateCannotSendReasonCodeError(request.reason_code)

        # エンティティの更新（変更された項目のみ）
        updated_reason = replace(
            reason,
            reason_code=request.reason_code if request.reason_code is not None else reason.reason_code,
            reason_name=request.reason_name if request.reason_name is not None else reason.reason_name,
            description=request.description if request.description is not None else reason.description,
            is_active=request.is_active if request.is_active is not None else reason.is_active,
        )

        # リポジトリで更新
        updated_reason = await self._repo.update(updated_reason)

        logger.info(
            "Cannot send reason updated successfully",
            extra={
                "event": "cannot_send_reason_updated",
                "reason_id": reason_id,
            },
        )

        return updated_reason

    async def delete_reason(
        self,
        reason_id: int,
    ) -> None:
        """
        送信不可理由を論理削除

        Args:
            reason_id: 送信不可理由ID

        Raises:
            CannotSendReasonNotFoundError: 送信不可理由が見つからない場合
        """
        # 存在確認
        reason = await self._repo.find_by_id(reason_id=reason_id)
        if reason is None:
            raise CannotSendReasonNotFoundError(reason_id)

        # 論理削除を実行
        await self._repo.soft_delete(reason_id=reason_id)

        logger.info(
            "Cannot send reason deleted successfully",
            extra={
                "event": "cannot_send_reason_deleted",
                "reason_id": reason_id,
                "reason_code": reason.reason_code,
            },
        )
