"""
スクリプト用スキーマ

APIリクエスト・レスポンス用のPydanticモデルを定義します。
入力バリデーション、NULL文字・制御文字のチェックを含みます。
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ListScriptBase(BaseModel):
    """スクリプトの基本スキーマ"""

    title: str = Field(
        min_length=1,
        max_length=255,
        description="スクリプトタイトル",
        examples=["初回アプローチ用スクリプト"],
    )
    content: str = Field(
        min_length=1,
        max_length=10000,  # DoS攻撃対策として10,000文字に制限（A4用紙約5ページ分）
        description="スクリプト本文（営業トークの台本）",
        examples=["お世話になっております。〇〇社の△△と申します。"],
    )

    @field_validator("title", "content")
    @classmethod
    def validate_no_null_characters(cls, v: str) -> str:
        """
        NULL文字や危険な制御文字をチェック

        セキュリティ上の理由から、以下の文字を禁止します：
        - NULL文字 (\x00): SQLインジェクションやファイルパス攻撃に使用される可能性
        - 制御文字 (\x00-\x1F, \x7F): 改行・タブを除く制御文字
        """
        if "\x00" in v:
            raise ValueError("NULL文字は使用できません")

        # 制御文字のチェック（改行・タブ・復帰は許可）
        if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", v):
            raise ValueError("制御文字は使用できません")

        # 前後の空白を除去
        return v.strip()


class ListScriptCreate(ListScriptBase):
    """スクリプト作成用スキーマ"""

    list_id: int = Field(gt=0, description="リストID")


class ListScriptUpdate(BaseModel):
    """
    スクリプト更新用スキーマ

    部分更新をサポートするため、すべてのフィールドをOptionalにしています。
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="スクリプトタイトル",
    )
    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10000,  # DoS攻撃対策として10,000文字に制限
        description="スクリプト本文",
    )

    @field_validator("title", "content")
    @classmethod
    def validate_no_null_characters(cls, v: Optional[str]) -> Optional[str]:
        """NULL文字や制御文字をチェック"""
        if v is None:
            return v

        if "\x00" in v:
            raise ValueError("NULL文字は使用できません")

        if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", v):
            raise ValueError("制御文字は使用できません")

        return v.strip()


class ListScriptResponse(ListScriptBase):
    """スクリプトレスポンス用スキーマ"""

    id: int = Field(description="スクリプトID")
    list_id: int = Field(description="リストID")
    created_at: datetime = Field(description="作成日時")
    updated_at: datetime = Field(description="更新日時")
    deleted_at: Optional[datetime] = Field(None, description="削除日時")

    model_config = ConfigDict(from_attributes=True)


class ListScriptListResponse(BaseModel):
    """スクリプト一覧レスポンス用スキーマ"""

    scripts: list[ListScriptResponse] = Field(description="スクリプト一覧")
    total: int = Field(description="総件数")

    model_config = ConfigDict(from_attributes=True)
