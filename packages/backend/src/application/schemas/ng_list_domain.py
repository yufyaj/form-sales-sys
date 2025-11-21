"""
NGリストドメインスキーマ定義（Pydantic）

API送受信用のDTOスキーマを定義します。
バリデーションとデータ変換を担当します。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.infrastructure.utils.domain_utils import normalize_domain_pattern, is_wildcard_pattern


# リクエストスキーマ
class NgListDomainCreateRequest(BaseModel):
    """NGドメイン登録リクエスト"""

    list_id: int = Field(
        ...,
        gt=0,
        description="リストID",
        examples=[1],
    )
    domain: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="NGドメインパターン（ワイルドカード対応: *.example.com）",
        examples=["example.com", "*.example.com", "sub.example.com"],
    )
    memo: str | None = Field(
        None,
        max_length=500,
        description="メモ（任意）",
        examples=["競合他社のため送信禁止"],
    )

    @field_validator("domain")
    @classmethod
    def validate_and_normalize_domain(cls, v: str) -> str:
        """ドメインのバリデーションと正規化"""
        # 制御文字除去
        cleaned = "".join(c for c in v if c.isprintable() and not c.isspace())

        # 小文字化
        cleaned = cleaned.lower()

        # 基本的なドメイン形式チェック
        if not cleaned:
            raise ValueError("ドメインが空です")

        # ワイルドカード以外の特殊文字チェック
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789.-*")
        if not all(c in allowed_chars for c in cleaned):
            raise ValueError("ドメインに使用できない文字が含まれています")

        # ワイルドカードの位置チェック（先頭のみ許可）
        if '*' in cleaned:
            if not cleaned.startswith('*.'):
                raise ValueError("ワイルドカードは先頭の *.domain.com 形式のみ許可されます")
            # *.以降にワイルドカードがないかチェック
            if cleaned[2:].count('*') > 0:
                raise ValueError("ワイルドカードは先頭にのみ使用できます")
            # *.のみは不可
            if len(cleaned) <= 2:
                raise ValueError("ワイルドカード指定が不正です")

        # www.プレフィックスを除去（正規化）
        # ただし、*.www.example.comのようなパターンは許可
        if cleaned.startswith('www.') and not cleaned.startswith('*.'):
            cleaned = cleaned[4:]

        # 最終チェック: 空でないことを確認
        if not cleaned or cleaned == '*.':
            raise ValueError("有効なドメインを入力してください")

        return cleaned

    @field_validator("memo")
    @classmethod
    def sanitize_memo(cls, v: str | None) -> str | None:
        """メモのサニタイゼーション"""
        if v is None:
            return None
        # 制御文字除去（改行・タブは許可）
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned.strip() else None


class NgListDomainCheckRequest(BaseModel):
    """NGドメインチェックリクエスト"""

    list_id: int = Field(
        ...,
        gt=0,
        description="リストID",
        examples=[1],
    )
    url: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="チェック対象のURL",
        examples=["https://www.example.com/form", "http://example.com", "www.example.com"],
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """URLの基本的なバリデーション"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("URLが空です")

        # 明らかに不正な形式をチェック
        if not any(c in cleaned for c in ['.', '/']):
            raise ValueError("有効なURLを入力してください")

        return cleaned


# レスポンススキーマ
class NgListDomainResponse(BaseModel):
    """NGドメインレスポンス"""

    id: int = Field(..., description="NGドメインID")
    list_id: int = Field(..., description="リストID")
    domain: str = Field(..., description="元のドメインパターン（ユーザー入力）")
    domain_pattern: str = Field(..., description="正規化されたドメインパターン（比較用）")
    is_wildcard: bool = Field(..., description="ワイルドカード使用フラグ")
    memo: str | None = Field(None, description="メモ（任意）")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（ソフトデリート）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "list_id": 1,
                "domain": "*.example.com",
                "domain_pattern": "*.example.com",
                "is_wildcard": True,
                "memo": "競合他社のため送信禁止",
                "created_at": "2025-11-21T00:00:00Z",
                "updated_at": "2025-11-21T00:00:00Z",
                "deleted_at": None,
            }
        },
    )


class NgListDomainListResponse(BaseModel):
    """NGドメイン一覧レスポンス"""

    ng_domains: list[NgListDomainResponse] = Field(..., description="NGドメイン配列")
    total: int = Field(..., description="総件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ng_domains": [
                    {
                        "id": 1,
                        "list_id": 1,
                        "domain": "*.example.com",
                        "domain_pattern": "*.example.com",
                        "is_wildcard": True,
                        "memo": "競合他社のため送信禁止",
                        "created_at": "2025-11-21T00:00:00Z",
                        "updated_at": "2025-11-21T00:00:00Z",
                        "deleted_at": None,
                    },
                    {
                        "id": 2,
                        "list_id": 1,
                        "domain": "test.com",
                        "domain_pattern": "test.com",
                        "is_wildcard": False,
                        "memo": None,
                        "created_at": "2025-11-21T00:10:00Z",
                        "updated_at": "2025-11-21T00:10:00Z",
                        "deleted_at": None,
                    },
                ],
                "total": 2,
            }
        },
    )


class NgListDomainCheckResponse(BaseModel):
    """NGドメインチェックレスポンス"""

    is_ng: bool = Field(..., description="NGリストに含まれるか")
    matched_pattern: str | None = Field(
        None,
        description="マッチしたNGパターン（NGの場合のみ）",
    )
    extracted_domain: str | None = Field(
        None,
        description="URLから抽出されたドメイン",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_ng": True,
                "matched_pattern": "*.example.com",
                "extracted_domain": "sub.example.com",
            }
        },
    )
