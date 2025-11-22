"""
リストスクリプトエンティティ

ドメイン層のリストスクリプトモデル。リストごとの営業トーク台本を管理します。
インフラストラクチャ（データベース）から独立しています。
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListScriptEntity:
    """
    リストスクリプトエンティティ

    リストごとに設定される営業トーク台本をビジネスロジックの観点から表現します。
    各スクリプトは特定のリストに紐付きます。
    """

    id: int
    list_id: int  # FK to lists.id
    title: str  # スクリプトタイトル
    content: str  # スクリプト本文（営業トークの台本）
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def is_deleted(self) -> bool:
        """論理削除されているかを判定"""
        return self.deleted_at is not None

    def has_content(self) -> bool:
        """コンテンツが設定されているかを判定"""
        return bool(self.content and self.content.strip())

    def get_content_preview(self, max_length: int = 100) -> str:
        """
        コンテンツのプレビューを取得

        Args:
            max_length: プレビューの最大文字数

        Returns:
            プレビューテキスト（長い場合は省略記号付き）
        """
        if not self.has_content():
            return ""

        content_stripped = self.content.strip()
        if len(content_stripped) <= max_length:
            return content_stripped

        return content_stripped[:max_length] + "..."

    def validate_title(self) -> None:
        """
        タイトルの妥当性を検証

        Raises:
            ValueError: タイトルが空の場合
        """
        if not self.title or not self.title.strip():
            raise ValueError("スクリプトタイトルは必須です")

    def validate_content(self) -> None:
        """
        コンテンツの妥当性を検証

        Raises:
            ValueError: コンテンツが空の場合
        """
        if not self.content or not self.content.strip():
            raise ValueError("スクリプトコンテンツは必須です")

    def validate(self) -> None:
        """
        リストスクリプトエンティティの全バリデーションを実行

        Raises:
            ValueError: バリデーションエラー
        """
        self.validate_title()
        self.validate_content()
