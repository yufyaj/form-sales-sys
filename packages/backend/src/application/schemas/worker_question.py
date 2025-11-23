"""
ワーカー質問関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.infrastructure.persistence.models.worker_question import QuestionPriority, QuestionStatus


# ========================================
# リクエストスキーマ
# ========================================


class WorkerQuestionCreateRequest(BaseModel):
    """ワーカー質問作成リクエスト"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="質問タイトル",
        examples=["フォーム入力の手順について"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description="質問内容",
        examples=["〇〇フォームの入力手順がわからないため、教えていただけますでしょうか。"],
    )
    client_organization_id: int | None = Field(
        None,
        description="関連する顧客組織ID（オプション）",
        examples=[1],
    )
    priority: QuestionPriority = Field(
        default=QuestionPriority.MEDIUM,
        description="質問優先度",
        examples=[QuestionPriority.MEDIUM],
    )
    tags: str | None = Field(
        None,
        max_length=500,
        description="タグ（JSON配列形式、オプション）",
        examples=['["フォーム入力", "操作方法"]'],
    )


class WorkerQuestionUpdateRequest(BaseModel):
    """ワーカー質問更新リクエスト"""

    title: str | None = Field(
        None,
        min_length=1,
        max_length=500,
        description="質問タイトル",
        examples=["フォーム入力の手順について（修正）"],
    )
    content: str | None = Field(
        None,
        min_length=1,
        description="質問内容",
        examples=["〇〇フォームの〇〇項目の入力手順がわからないため、教えていただけますでしょうか。"],
    )
    status: QuestionStatus | None = Field(
        None,
        description="質問ステータス",
        examples=[QuestionStatus.IN_REVIEW],
    )
    priority: QuestionPriority | None = Field(
        None,
        description="質問優先度",
        examples=[QuestionPriority.HIGH],
    )
    tags: str | None = Field(
        None,
        max_length=500,
        description="タグ（JSON配列形式、オプション）",
        examples=['["フォーム入力", "操作方法", "緊急"]'],
    )
    internal_notes: str | None = Field(
        None,
        max_length=2000,
        description="営業支援会社用の内部メモ",
        examples=["この質問は〇〇案件に関連しています"],
    )


class WorkerQuestionAnswerRequest(BaseModel):
    """ワーカー質問回答リクエスト"""

    answer: str = Field(
        ...,
        min_length=1,
        description="回答内容",
        examples=["〇〇フォームの入力手順は以下の通りです。\n1. ・・・\n2. ・・・"],
    )


# ========================================
# レスポンススキーマ
# ========================================


class WorkerQuestionResponse(BaseModel):
    """ワーカー質問レスポンス"""

    id: int = Field(..., description="質問ID")
    worker_id: int = Field(..., description="質問者のワーカーID")
    organization_id: int = Field(..., description="営業支援会社の組織ID")
    client_organization_id: int | None = Field(None, description="関連する顧客組織ID")
    title: str = Field(..., description="質問タイトル")
    content: str = Field(..., description="質問内容")
    status: QuestionStatus = Field(..., description="質問ステータス")
    priority: QuestionPriority = Field(..., description="質問優先度")
    answer: str | None = Field(None, description="回答内容")
    answered_by_user_id: int | None = Field(None, description="回答者のユーザーID")
    answered_at: datetime | None = Field(None, description="回答日時")
    tags: str | None = Field(None, description="タグ（JSON配列形式）")
    internal_notes: str | None = Field(None, description="営業支援会社用の内部メモ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "worker_id": 1,
                "organization_id": 1,
                "client_organization_id": 1,
                "title": "フォーム入力の手順について",
                "content": "〇〇フォームの入力手順がわからないため、教えていただけますでしょうか。",
                "status": "pending",
                "priority": "medium",
                "answer": None,
                "answered_by_user_id": None,
                "answered_at": None,
                "tags": '["フォーム入力", "操作方法"]',
                "internal_notes": None,
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-22T10:00:00Z",
                "deleted_at": None,
            }
        },
    )


class WorkerQuestionListResponse(BaseModel):
    """ワーカー質問一覧レスポンス"""

    questions: list[WorkerQuestionResponse] = Field(..., description="質問リスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "questions": [
                    {
                        "id": 1,
                        "worker_id": 1,
                        "organization_id": 1,
                        "client_organization_id": 1,
                        "title": "フォーム入力の手順について",
                        "content": "〇〇フォームの入力手順がわからないため、教えていただけますでしょうか。",
                        "status": "pending",
                        "priority": "medium",
                        "answer": None,
                        "answered_by_user_id": None,
                        "answered_at": None,
                        "tags": '["フォーム入力", "操作方法"]',
                        "internal_notes": None,
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


class UnreadCountResponse(BaseModel):
    """未読質問数レスポンス"""

    unread_count: int = Field(..., description="未読質問数（pendingステータスの質問数）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "unread_count": 5,
            }
        },
    )
