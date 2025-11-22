"""
リストスクリプトリポジトリインターフェース

ドメイン層のリポジトリインターフェース定義。
インフラストラクチャ層で実装されます。
"""
from abc import ABC, abstractmethod

from src.domain.entities.list_script_entity import ListScriptEntity


class IListScriptRepository(ABC):
    """リストスクリプトリポジトリのインターフェース"""

    @abstractmethod
    async def create(
        self,
        list_id: int,
        title: str,
        content: str,
    ) -> ListScriptEntity:
        """
        スクリプトを作成

        Args:
            list_id: リストID
            title: スクリプトタイトル
            content: スクリプト本文

        Returns:
            作成されたスクリプトエンティティ
        """
        pass

    @abstractmethod
    async def get_by_id(self, script_id: int) -> ListScriptEntity | None:
        """
        IDでスクリプトを取得

        Args:
            script_id: スクリプトID

        Returns:
            スクリプトエンティティ（見つからない場合はNone）
        """
        pass

    @abstractmethod
    async def list_by_list_id(self, list_id: int) -> list[ListScriptEntity]:
        """
        リストIDでスクリプト一覧を取得

        Args:
            list_id: リストID

        Returns:
            スクリプトエンティティのリスト
        """
        pass

    @abstractmethod
    async def update(
        self,
        script_id: int,
        title: str | None = None,
        content: str | None = None,
    ) -> ListScriptEntity | None:
        """
        スクリプトを更新

        Args:
            script_id: スクリプトID
            title: 新しいタイトル（Noneの場合は更新しない）
            content: 新しいコンテンツ（Noneの場合は更新しない）

        Returns:
            更新されたスクリプトエンティティ（見つからない場合はNone）
        """
        pass

    @abstractmethod
    async def delete(self, script_id: int) -> bool:
        """
        スクリプトを論理削除

        Args:
            script_id: スクリプトID

        Returns:
            削除成功した場合True、見つからない場合False
        """
        pass

    @abstractmethod
    async def exists(self, script_id: int) -> bool:
        """
        スクリプトが存在するかチェック

        Args:
            script_id: スクリプトID

        Returns:
            存在する場合True
        """
        pass
