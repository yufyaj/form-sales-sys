"""
プロジェクト関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ========================================
# Enum
# ========================================


class ProjectStatusEnum(str, Enum):
    """プロジェクトステータス"""

    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriorityEnum(str, Enum):
    """プロジェクト優先度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ========================================
# 基底スキーマ
# ========================================


class ProjectBase(BaseModel):
    """プロジェクトスキーマの基底クラス"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="プロジェクト名（最大255文字）",
        examples=["新規Webサイト構築"],
    )
    description: str | None = Field(
        None,
        description="プロジェクト説明",
        examples=["コーポレートサイトのリニューアル"],
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """
        プロジェクト名をサニタイズ

        制御文字を削除し、空白を正規化する
        """
        # 制御文字を削除
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        # 連続する空白を1つにする
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("プロジェクト名は空にできません")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """
        プロジェクト説明をサニタイズ

        制御文字を削除する
        """
        if v is None:
            return None
        # 制御文字を削除（タブと改行は許可）
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


# ========================================
# リクエストスキーマ
# ========================================


class ProjectCreateRequest(ProjectBase):
    """プロジェクト作成リクエスト"""

    client_organization_id: int = Field(
        ...,
        gt=0,
        description="顧客組織ID",
    )
    status: ProjectStatusEnum = Field(
        default=ProjectStatusEnum.PLANNING,
        description="プロジェクトステータス",
    )
    start_date: date | None = Field(
        None,
        description="開始予定日",
    )
    end_date: date | None = Field(
        None,
        description="終了予定日",
    )
    estimated_budget: int | None = Field(
        None,
        ge=0,
        description="見積予算（円）",
    )
    actual_budget: int | None = Field(
        None,
        ge=0,
        description="実績予算（円）",
    )
    priority: ProjectPriorityEnum | None = Field(
        None,
        description="プロジェクト優先度",
    )
    owner_user_id: int | None = Field(
        None,
        gt=0,
        description="プロジェクトオーナー（担当ユーザーID）",
    )
    notes: str | None = Field(
        None,
        description="備考",
    )

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, v: str | None) -> str | None:
        """備考をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


class ProjectUpdateRequest(BaseModel):
    """プロジェクト更新リクエスト"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="プロジェクト名（最大255文字）",
    )
    description: str | None = Field(
        None,
        description="プロジェクト説明",
    )
    status: ProjectStatusEnum | None = Field(
        None,
        description="プロジェクトステータス",
    )
    start_date: date | None = Field(
        None,
        description="開始予定日",
    )
    end_date: date | None = Field(
        None,
        description="終了予定日",
    )
    estimated_budget: int | None = Field(
        None,
        ge=0,
        description="見積予算（円）",
    )
    actual_budget: int | None = Field(
        None,
        ge=0,
        description="実績予算（円）",
    )
    priority: ProjectPriorityEnum | None = Field(
        None,
        description="プロジェクト優先度",
    )
    owner_user_id: int | None = Field(
        None,
        gt=0,
        description="プロジェクトオーナー（担当ユーザーID）",
    )
    notes: str | None = Field(
        None,
        description="備考",
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """プロジェクト名をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("プロジェクト名は空にできません")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """プロジェクト説明をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None

    @field_validator("notes")
    @classmethod
    def sanitize_notes(cls, v: str | None) -> str | None:
        """備考をサニタイズ"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


# ========================================
# レスポンススキーマ
# ========================================


class ProjectResponse(BaseModel):
    """プロジェクトレスポンス"""

    id: int = Field(..., description="プロジェクトID")
    client_organization_id: int = Field(..., description="顧客組織ID")
    name: str = Field(..., description="プロジェクト名")
    description: str | None = Field(None, description="プロジェクト説明")
    status: ProjectStatusEnum = Field(..., description="プロジェクトステータス")
    start_date: date | None = Field(None, description="開始予定日")
    end_date: date | None = Field(None, description="終了予定日")
    estimated_budget: int | None = Field(None, description="見積予算（円）")
    actual_budget: int | None = Field(None, description="実績予算（円）")
    priority: ProjectPriorityEnum | None = Field(None, description="プロジェクト優先度")
    owner_user_id: int | None = Field(None, description="プロジェクトオーナー（担当ユーザーID）")
    notes: str | None = Field(None, description="備考")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,  # エンティティから変換可能にする
        json_schema_extra={
            "example": {
                "id": 1,
                "client_organization_id": 10,
                "name": "新規Webサイト構築",
                "description": "コーポレートサイトのリニューアル",
                "status": "in_progress",
                "start_date": "2025-01-01",
                "end_date": "2025-03-31",
                "estimated_budget": 5000000,
                "actual_budget": 4800000,
                "priority": "high",
                "owner_user_id": 5,
                "notes": "Q1完了目標",
                "created_at": "2025-11-03T10:00:00Z",
                "updated_at": "2025-11-10T15:30:00Z",
                "deleted_at": None,
            }
        },
    )


class ProjectListResponse(BaseModel):
    """プロジェクト一覧レスポンス"""

    projects: list[ProjectResponse] = Field(..., description="プロジェクトリスト")
    total: int = Field(..., description="総件数")
    page: int = Field(..., ge=1, description="現在のページ番号（1始まり）")
    page_size: int = Field(..., ge=1, le=100, description="ページサイズ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "projects": [
                    {
                        "id": 1,
                        "client_organization_id": 10,
                        "name": "新規Webサイト構築",
                        "description": "コーポレートサイトのリニューアル",
                        "status": "in_progress",
                        "start_date": "2025-01-01",
                        "end_date": "2025-03-31",
                        "estimated_budget": 5000000,
                        "actual_budget": 4800000,
                        "priority": "high",
                        "owner_user_id": 5,
                        "notes": "Q1完了目標",
                        "created_at": "2025-11-03T10:00:00Z",
                        "updated_at": "2025-11-10T15:30:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 20,
            }
        },
    )
