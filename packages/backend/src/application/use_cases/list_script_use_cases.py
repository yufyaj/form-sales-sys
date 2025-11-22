"""
リストスクリプト管理ユースケース

リストスクリプトのCRUD操作とビジネスロジックを実行します。
"""

import logging

from src.application.schemas.list_script import (
    ListScriptCreate,
    ListScriptUpdate,
)
from src.domain.entities.list_script_entity import ListScriptEntity
from src.domain.exceptions import (
    ListNotFoundError,
    ListScriptNotFoundError,
)
from src.domain.interfaces.list_repository import IListRepository
from src.domain.interfaces.list_script_repository import IListScriptRepository

logger = logging.getLogger(__name__)


class ListScriptUseCases:
    """リストスクリプト管理ユースケースクラス"""

    def __init__(
        self,
        list_script_repository: IListScriptRepository,
        list_repository: IListRepository,
    ) -> None:
        """
        Args:
            list_script_repository: リストスクリプトリポジトリ
            list_repository: リストリポジトリ（リスト存在確認用）
        """
        self._script_repo = list_script_repository
        self._list_repo = list_repository

    async def create_script(
        self,
        requesting_organization_id: int,
        request: ListScriptCreate,
    ) -> ListScriptEntity:
        """
        スクリプトを作成

        Args:
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            request: スクリプト作成リクエスト

        Returns:
            作成されたスクリプトエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
        """
        # セキュリティ: リストの存在確認と権限チェック
        list_entity = await self._list_repo.find_by_id(
            list_id=request.list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            # セキュリティログ: 権限エラー
            logger.warning(
                "Unauthorized access attempt to list",
                extra={
                    "event": "list_script_unauthorized_access",
                    "organization_id": requesting_organization_id,
                    "list_id": request.list_id,
                    "action": "create_script",
                }
            )
            raise ListNotFoundError(request.list_id)

        # スクリプトを作成
        script = await self._script_repo.create(
            list_id=request.list_id,
            title=request.title,
            content=request.content,
        )

        # セキュリティログ: 成功
        logger.info(
            "List script created successfully",
            extra={
                "event": "list_script_created",
                "organization_id": requesting_organization_id,
                "list_id": request.list_id,
                "script_id": script.id,
                "title": script.title,
            }
        )

        return script

    async def get_script(
        self,
        script_id: int,
        requesting_organization_id: int,
    ) -> ListScriptEntity:
        """
        スクリプトを取得

        Args:
            script_id: スクリプトID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Returns:
            スクリプトエンティティ

        Raises:
            ListScriptNotFoundError: スクリプトが見つからない場合
        """
        script = await self._script_repo.get_by_id(script_id)

        if script is None:
            raise ListScriptNotFoundError(script_id)

        # セキュリティ: 組織の権限チェック（スクリプトが属するリストの組織を確認）
        list_entity = await self._list_repo.find_by_id(
            list_id=script.list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            # セキュリティログ: 権限エラー
            logger.warning(
                "Unauthorized access attempt to list script",
                extra={
                    "event": "list_script_unauthorized_access",
                    "organization_id": requesting_organization_id,
                    "script_id": script_id,
                    "action": "get_script",
                }
            )
            raise ListScriptNotFoundError(script_id)

        return script

    async def list_scripts_by_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> list[ListScriptEntity]:
        """
        リストに属するスクリプトの一覧を取得

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Returns:
            スクリプトエンティティのリスト

        Raises:
            ListNotFoundError: リストが見つからない場合
        """
        # セキュリティ: リストの存在確認と権限チェック
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # スクリプト一覧を取得
        scripts = await self._script_repo.list_by_list_id(list_id=list_id)

        return scripts

    async def update_script(
        self,
        script_id: int,
        requesting_organization_id: int,
        request: ListScriptUpdate,
    ) -> ListScriptEntity:
        """
        スクリプトを更新

        Args:
            script_id: スクリプトID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            request: スクリプト更新リクエスト

        Returns:
            更新されたスクリプトエンティティ

        Raises:
            ListScriptNotFoundError: スクリプトが見つからない場合
        """
        # 存在確認（権限チェックを含む）
        script = await self.get_script(script_id, requesting_organization_id)

        # 更新を実行
        updated_script = await self._script_repo.update(
            script_id=script_id,
            title=request.title,
            content=request.content,
        )

        if updated_script is None:
            raise ListScriptNotFoundError(script_id)

        # セキュリティログ: 更新成功
        logger.info(
            "List script updated successfully",
            extra={
                "event": "list_script_updated",
                "organization_id": requesting_organization_id,
                "script_id": script_id,
                "list_id": script.list_id,
            }
        )

        return updated_script

    async def delete_script(
        self,
        script_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        スクリプトを論理削除

        Args:
            script_id: スクリプトID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Raises:
            ListScriptNotFoundError: スクリプトが見つからない場合
        """
        # 存在確認（権限チェックを含む）
        script = await self.get_script(script_id, requesting_organization_id)

        # 論理削除を実行
        success = await self._script_repo.delete(script_id=script_id)

        if not success:
            raise ListScriptNotFoundError(script_id)

        # セキュリティログ: 削除成功
        logger.info(
            "List script deleted successfully",
            extra={
                "event": "list_script_deleted",
                "organization_id": requesting_organization_id,
                "script_id": script_id,
                "list_id": script.list_id,
                "title": script.title,
            }
        )
