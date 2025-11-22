"""
ワーカー関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.persistence.models.worker import SkillLevel, WorkerStatus


# ========================================
# 基底スキーマ
# ========================================


class WorkerBase(BaseModel):
    """ワーカースキーマの基底クラス"""

    status: WorkerStatus = Field(
        ...,
        description="ワーカーステータス",
        examples=[WorkerStatus.ACTIVE],
    )
    skill_level: SkillLevel | None = Field(
        None,
        description="スキルレベル",
        examples=[SkillLevel.INTERMEDIATE],
    )
    experience_months: int | None = Field(
        None,
        ge=0,
        description="経験月数",
        examples=[12],
    )
    specialties: str | None = Field(
        None,
        max_length=500,
        description="得意分野・専門領域",
        examples=["BtoB営業、IT業界"],
    )
    max_tasks_per_day: int | None = Field(
        None,
        ge=0,
        description="1日の最大タスク数",
        examples=[10],
    )
    available_hours_per_week: int | None = Field(
        None,
        ge=0,
        description="週間稼働可能時間",
        examples=[40],
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="管理者用メモ・備考",
        examples=["経験豊富なワーカー"],
    )


# ========================================
# リクエストスキーマ
# ========================================


class WorkerCreateRequest(BaseModel):
    """ワーカー作成リクエスト"""

    user_id: int = Field(
        ...,
        description="ユーザーID（対応するUserレコードのID）",
        examples=[1],
    )
    status: WorkerStatus = Field(
        default=WorkerStatus.PENDING,
        description="ワーカーステータス",
        examples=[WorkerStatus.PENDING],
    )
    skill_level: SkillLevel | None = Field(
        None,
        description="スキルレベル",
        examples=[SkillLevel.INTERMEDIATE],
    )
    experience_months: int | None = Field(
        None,
        ge=0,
        description="経験月数",
        examples=[12],
    )
    specialties: str | None = Field(
        None,
        max_length=500,
        description="得意分野・専門領域",
        examples=["BtoB営業、IT業界"],
    )
    max_tasks_per_day: int | None = Field(
        None,
        ge=0,
        description="1日の最大タスク数",
        examples=[10],
    )
    available_hours_per_week: int | None = Field(
        None,
        ge=0,
        description="週間稼働可能時間",
        examples=[40],
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="管理者用メモ・備考",
        examples=["新規登録ワーカー"],
    )


class WorkerUpdateRequest(BaseModel):
    """ワーカー更新リクエスト"""

    status: WorkerStatus | None = Field(
        None,
        description="ワーカーステータス",
        examples=[WorkerStatus.ACTIVE],
    )
    skill_level: SkillLevel | None = Field(
        None,
        description="スキルレベル",
        examples=[SkillLevel.ADVANCED],
    )
    experience_months: int | None = Field(
        None,
        ge=0,
        description="経験月数",
        examples=[24],
    )
    specialties: str | None = Field(
        None,
        max_length=500,
        description="得意分野・専門領域",
        examples=["BtoB営業、IT業界、SaaS"],
    )
    max_tasks_per_day: int | None = Field(
        None,
        ge=0,
        description="1日の最大タスク数",
        examples=[15],
    )
    available_hours_per_week: int | None = Field(
        None,
        ge=0,
        description="週間稼働可能時間",
        examples=[50],
    )
    completed_tasks_count: int | None = Field(
        None,
        ge=0,
        description="完了タスク数",
        examples=[100],
    )
    success_rate: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="成功率（%）",
        examples=[85.5],
    )
    average_task_time_minutes: int | None = Field(
        None,
        ge=0,
        description="平均タスク処理時間（分）",
        examples=[30],
    )
    rating: float | None = Field(
        None,
        ge=0.0,
        le=5.0,
        description="評価スコア（5段階）",
        examples=[4.5],
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="管理者用メモ・備考",
        examples=["パフォーマンス向上"],
    )


# ========================================
# レスポンススキーマ
# ========================================


class WorkerResponse(BaseModel):
    """ワーカーレスポンス"""

    id: int = Field(..., description="ワーカーID")
    user_id: int = Field(..., description="ユーザーID")
    organization_id: int = Field(..., description="所属組織ID（営業支援会社）")
    status: WorkerStatus = Field(..., description="ワーカーステータス")
    skill_level: SkillLevel | None = Field(None, description="スキルレベル")
    experience_months: int | None = Field(None, description="経験月数")
    specialties: str | None = Field(None, description="得意分野・専門領域")
    max_tasks_per_day: int | None = Field(None, description="1日の最大タスク数")
    available_hours_per_week: int | None = Field(None, description="週間稼働可能時間")
    completed_tasks_count: int = Field(..., description="完了タスク数")
    success_rate: float | None = Field(None, description="成功率（%）")
    average_task_time_minutes: int | None = Field(None, description="平均タスク処理時間（分）")
    rating: float | None = Field(None, description="評価スコア（5段階）")
    notes: str | None = Field(None, description="管理者用メモ・備考")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "organization_id": 1,
                "status": "active",
                "skill_level": "intermediate",
                "experience_months": 12,
                "specialties": "BtoB営業、IT業界",
                "max_tasks_per_day": 10,
                "available_hours_per_week": 40,
                "completed_tasks_count": 50,
                "success_rate": 85.5,
                "average_task_time_minutes": 30,
                "rating": 4.5,
                "notes": "優秀なワーカー",
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-22T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class WorkerListResponse(BaseModel):
    """ワーカー一覧レスポンス"""

    workers: list[WorkerResponse] = Field(..., description="ワーカーリスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workers": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "organization_id": 1,
                        "status": "active",
                        "skill_level": "intermediate",
                        "experience_months": 12,
                        "specialties": "BtoB営業、IT業界",
                        "max_tasks_per_day": 10,
                        "available_hours_per_week": 40,
                        "completed_tasks_count": 50,
                        "success_rate": 85.5,
                        "average_task_time_minutes": 30,
                        "rating": 4.5,
                        "notes": "優秀なワーカー",
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-22T10:00:00Z",
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
# ユーザー情報を含むレスポンス
# ========================================


class WorkerWithUserResponse(WorkerResponse):
    """ユーザー情報を含むワーカーレスポンス"""

    user_email: str = Field(..., description="ユーザーメールアドレス")
    user_full_name: str = Field(..., description="ユーザー氏名")
    user_phone: str | None = Field(None, description="ユーザー電話番号")
    user_is_active: bool = Field(..., description="ユーザーアクティブフラグ")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "organization_id": 1,
                "status": "active",
                "skill_level": "intermediate",
                "experience_months": 12,
                "specialties": "BtoB営業、IT業界",
                "max_tasks_per_day": 10,
                "available_hours_per_week": 40,
                "completed_tasks_count": 50,
                "success_rate": 85.5,
                "average_task_time_minutes": 30,
                "rating": 4.5,
                "notes": "優秀なワーカー",
                "user_email": "worker@example.com",
                "user_full_name": "山田太郎",
                "user_phone": "090-1234-5678",
                "user_is_active": True,
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-22T10:00:00Z",
                "deleted_at": None,
            }
        },
    )
