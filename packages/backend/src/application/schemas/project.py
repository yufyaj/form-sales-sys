"""
プロジェクト関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.entities.project_entity import ProjectStatus


# ========================================
# 基底スキーマ
# ========================================


class ProjectBase(BaseModel):
    """プロジェクトスキーマの基底クラス"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="プロジェクト名",
        examples=["新規Webサイト構築プロジェクト"],
    )
    description: str | None = Field(
        None,
        description="プロジェクトの説明",
        examples=["新しいコーポレートサイトの構築"],
    )


# ========================================
# リクエストスキーマ
# ========================================


class ProjectCreateRequest(ProjectBase):
    """プロジェクト作成リクエスト"""

    client_organization_id: int = Field(
        ...,
        description="顧客組織ID",
        examples=[1],
    )
    status: ProjectStatus = Field(
        ProjectStatus.PLANNING,
        description="プロジェクトステータス",
        examples=[ProjectStatus.PLANNING],
    )
    start_date: date | None = Field(
        None,
        description="開始日",
        examples=["2025-04-01"],
    )
    end_date: date | None = Field(
        None,
        description="終了日",
        examples=["2025-09-30"],
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info) -> date | None:
        """
        終了日のバリデーション

        開始日が指定されている場合、終了日は開始日以降である必要があります。
        """
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]
            if start_date is not None and v < start_date:
                raise ValueError("終了日は開始日以降の日付を指定してください")
        return v


class ProjectUpdateRequest(BaseModel):
    """プロジェクト更新リクエスト"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="プロジェクト名",
        examples=["更新後のプロジェクト名"],
    )
    client_organization_id: int | None = Field(
        None,
        description="顧客組織ID",
        examples=[1],
    )
    status: ProjectStatus | None = Field(
        None,
        description="プロジェクトステータス",
        examples=[ProjectStatus.ACTIVE],
    )
    start_date: date | None = Field(
        None,
        description="開始日",
        examples=["2025-04-01"],
    )
    end_date: date | None = Field(
        None,
        description="終了日",
        examples=["2025-09-30"],
    )
    description: str | None = Field(
        None,
        description="プロジェクトの説明",
        examples=["更新された説明"],
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info) -> date | None:
        """
        終了日のバリデーション

        開始日が指定されている場合、終了日は開始日以降である必要があります。
        """
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]
            if start_date is not None and v < start_date:
                raise ValueError("終了日は開始日以降の日付を指定してください")
        return v


# ========================================
# レスポンススキーマ
# ========================================


class ProjectResponse(ProjectBase):
    """プロジェクトレスポンス"""

    id: int = Field(..., description="プロジェクトID")
    client_organization_id: int = Field(..., description="顧客組織ID")
    sales_support_organization_id: int = Field(..., description="営業支援会社組織ID")
    status: ProjectStatus = Field(..., description="プロジェクトステータス")
    start_date: date | None = Field(None, description="開始日")
    end_date: date | None = Field(None, description="終了日")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,  # SQLAlchemyモデルから変換可能にする
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "新規Webサイト構築プロジェクト",
                "client_organization_id": 1,
                "sales_support_organization_id": 1,
                "status": "planning",
                "start_date": "2025-04-01",
                "end_date": "2025-09-30",
                "description": "新しいコーポレートサイトの構築",
                "created_at": "2025-11-16T10:00:00Z",
                "updated_at": "2025-11-16T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class ProjectListResponse(BaseModel):
    """プロジェクト一覧レスポンス"""

    projects: list[ProjectResponse] = Field(..., description="プロジェクトリスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "projects": [
                    {
                        "id": 1,
                        "name": "新規Webサイト構築プロジェクト",
                        "client_organization_id": 1,
                        "sales_support_organization_id": 1,
                        "status": "planning",
                        "start_date": "2025-04-01",
                        "end_date": "2025-09-30",
                        "description": "新しいコーポレートサイトの構築",
                        "created_at": "2025-11-16T10:00:00Z",
                        "updated_at": "2025-11-16T10:00:00Z",
                        "deleted_at": None,
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100,
            }
        },
    )


# ========================================
# 拡張レスポンススキーマ（顧客組織情報を含む）
# ========================================


class ProjectWithClientResponse(ProjectResponse):
    """顧客組織情報を含むプロジェクトレスポンス"""

    client_organization_name: str | None = Field(
        None, description="顧客組織名"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "新規Webサイト構築プロジェクト",
                "client_organization_id": 1,
                "client_organization_name": "株式会社サンプル",
                "sales_support_organization_id": 1,
                "status": "planning",
                "start_date": "2025-04-01",
                "end_date": "2025-09-30",
                "description": "新しいコーポレートサイトの構築",
                "created_at": "2025-11-16T10:00:00Z",
                "updated_at": "2025-11-16T10:00:00Z",
                "deleted_at": None,
            }
        },
    )
