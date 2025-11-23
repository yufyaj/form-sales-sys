"""
作業記録関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.infrastructure.persistence.models.work_record import WorkRecordStatus


# ========================================
# 送信結果構造化スキーマ（JSONB注入対策）
# ========================================


class FormSubmissionResult(BaseModel):
    """
    送信結果の構造化スキーマ

    form_submission_resultフィールドのセキュリティ強化のため、
    許可されたフィールドのみを受け付ける構造化スキーマを定義します。
    これにより、JSONB注入攻撃やプロトタイプ汚染を防止します。
    """

    status_code: int | None = Field(
        None,
        ge=100,
        le=599,
        description="HTTPステータスコード",
        examples=[200],
    )
    message: str | None = Field(
        None,
        max_length=500,
        description="メッセージ",
        examples=["送信成功"],
    )
    response_time_ms: int | None = Field(
        None,
        ge=0,
        le=60000,
        description="レスポンスタイム（ミリ秒）",
        examples=[250],
    )
    screenshot_url: str | None = Field(
        None,
        max_length=1000,
        description="スクリーンショットURL",
        examples=["https://example.com/screenshots/123.png"],
    )
    error_message: str | None = Field(
        None,
        max_length=1000,
        description="エラーメッセージ",
        examples=["フォームが見つかりませんでした"],
    )
    retry_count: int | None = Field(
        None,
        ge=0,
        le=10,
        description="リトライ回数",
        examples=[0],
    )

    model_config = ConfigDict(
        # 追加フィールドを許可しない（厳格なバリデーション）
        extra="forbid",
        json_schema_extra={
            "example": {
                "status_code": 200,
                "message": "送信成功",
                "response_time_ms": 250,
                "screenshot_url": "https://example.com/screenshots/123.png",
                "error_message": None,
                "retry_count": 0,
            }
        },
    )


# ========================================
# リクエストスキーマ
# ========================================


class WorkRecordCreateRequest(BaseModel):
    """作業記録作成リクエスト"""

    assignment_id: int = Field(
        ...,
        description="リスト項目割り当てID",
        examples=[1],
    )
    worker_id: int = Field(
        ...,
        description="ワーカーID",
        examples=[1],
    )
    status: WorkRecordStatus = Field(
        ...,
        description="送信済み or 送信不可",
        examples=[WorkRecordStatus.SENT],
    )
    started_at: datetime = Field(
        ...,
        description="作業開始日時",
        examples=["2025-11-22T10:00:00Z"],
    )
    completed_at: datetime = Field(
        ...,
        description="作業完了日時",
        examples=["2025-11-22T10:30:00Z"],
    )
    form_submission_result: FormSubmissionResult | None = Field(
        None,
        description="送信結果の詳細（構造化スキーマ）",
        examples=[FormSubmissionResult(status_code=200, message="送信成功")],
    )
    cannot_send_reason_id: int | None = Field(
        None,
        description="送信不可理由ID（送信不可の場合のみ）",
        examples=[1],
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="メモ・備考",
        examples=["問題なく送信完了"],
    )

    @field_validator("completed_at")
    @classmethod
    def validate_completed_at(cls, v: datetime, info) -> datetime:
        """完了日時が開始日時より後であることを検証"""
        if "started_at" in info.data and v < info.data["started_at"]:
            raise ValueError("completed_at must be after started_at")
        return v

    @field_validator("form_submission_result")
    @classmethod
    def validate_submission_result_size(
        cls, v: FormSubmissionResult | None
    ) -> FormSubmissionResult | None:
        """送信結果のサイズ検証（10KB制限）"""
        if v is not None:
            # JSON文字列化してサイズチェック（10KB制限）
            json_str = json.dumps(v.model_dump())
            if len(json_str) > 10240:  # 10KB
                raise ValueError("form_submission_result exceeds maximum size of 10KB")
        return v

    @field_validator("cannot_send_reason_id")
    @classmethod
    def validate_cannot_send_reason_id(cls, v: int | None, info) -> int | None:
        """送信不可の場合は理由IDが必須であることを検証"""
        if "status" in info.data:
            status = info.data["status"]
            if status == WorkRecordStatus.CANNOT_SEND and v is None:
                raise ValueError("cannot_send_reason_id is required when status is CANNOT_SEND")
        return v


class WorkRecordUpdateRequest(BaseModel):
    """作業記録更新リクエスト"""

    status: WorkRecordStatus | None = Field(
        None,
        description="送信済み or 送信不可",
        examples=[WorkRecordStatus.SENT],
    )
    started_at: datetime | None = Field(
        None,
        description="作業開始日時",
        examples=["2025-11-22T10:00:00Z"],
    )
    completed_at: datetime | None = Field(
        None,
        description="作業完了日時",
        examples=["2025-11-22T10:30:00Z"],
    )
    form_submission_result: FormSubmissionResult | None = Field(
        None,
        description="送信結果の詳細（構造化スキーマ）",
        examples=[FormSubmissionResult(status_code=200, message="送信成功", retry_count=1)],
    )
    cannot_send_reason_id: int | None = Field(
        None,
        description="送信不可理由ID（送信不可の場合のみ）",
        examples=[1],
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="メモ・備考",
        examples=["再試行にて送信完了"],
    )

    @field_validator("form_submission_result")
    @classmethod
    def validate_submission_result_size(
        cls, v: FormSubmissionResult | None
    ) -> FormSubmissionResult | None:
        """送信結果のサイズ検証（10KB制限）"""
        if v is not None:
            # JSON文字列化してサイズチェック（10KB制限）
            json_str = json.dumps(v.model_dump())
            if len(json_str) > 10240:  # 10KB
                raise ValueError("form_submission_result exceeds maximum size of 10KB")
        return v


# ========================================
# レスポンススキーマ
# ========================================


class WorkRecordResponse(BaseModel):
    """作業記録レスポンス"""

    id: int = Field(..., description="作業記録ID")
    assignment_id: int = Field(..., description="リスト項目割り当てID")
    worker_id: int = Field(..., description="ワーカーID")
    status: WorkRecordStatus = Field(..., description="送信済み or 送信不可")
    started_at: datetime = Field(..., description="作業開始日時")
    completed_at: datetime = Field(..., description="作業完了日時")
    form_submission_result: dict[str, Any] | None = Field(None, description="送信結果の詳細")
    cannot_send_reason_id: int | None = Field(None, description="送信不可理由ID")
    notes: str | None = Field(None, description="メモ・備考")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    deleted_at: datetime | None = Field(None, description="削除日時（論理削除）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "assignment_id": 1,
                "worker_id": 1,
                "status": "sent",
                "started_at": "2025-11-22T10:00:00Z",
                "completed_at": "2025-11-22T10:30:00Z",
                "form_submission_result": {
                    "status_code": 200,
                    "message": "送信成功",
                    "response_time_ms": 250,
                },
                "cannot_send_reason_id": None,
                "notes": "問題なく送信完了",
                "created_at": "2025-11-22T10:30:00Z",
                "updated_at": "2025-11-22T10:30:00Z",
                "deleted_at": None,
            }
        },
    )


class WorkRecordListResponse(BaseModel):
    """作業記録一覧レスポンス"""

    records: list[WorkRecordResponse] = Field(..., description="作業記録リスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップした件数")
    limit: int = Field(..., description="取得した件数")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "records": [
                    {
                        "id": 1,
                        "assignment_id": 1,
                        "worker_id": 1,
                        "status": "sent",
                        "started_at": "2025-11-22T10:00:00Z",
                        "completed_at": "2025-11-22T10:30:00Z",
                        "form_submission_result": {
                            "status_code": 200,
                            "message": "送信成功",
                        },
                        "cannot_send_reason_id": None,
                        "notes": "問題なく送信完了",
                        "created_at": "2025-11-22T10:30:00Z",
                        "updated_at": "2025-11-22T10:30:00Z",
                        "deleted_at": None,
                    },
                    {
                        "id": 2,
                        "assignment_id": 2,
                        "worker_id": 1,
                        "status": "cannot_send",
                        "started_at": "2025-11-22T11:00:00Z",
                        "completed_at": "2025-11-22T11:15:00Z",
                        "form_submission_result": None,
                        "cannot_send_reason_id": 1,
                        "notes": "フォームが見つからず",
                        "created_at": "2025-11-22T11:15:00Z",
                        "updated_at": "2025-11-22T11:15:00Z",
                        "deleted_at": None,
                    },
                ],
                "total": 2,
                "skip": 0,
                "limit": 100,
            }
        },
    )


# ========================================
# 詳細情報を含むレスポンス
# ========================================


class WorkRecordWithDetailsResponse(WorkRecordResponse):
    """送信不可理由の詳細を含む作業記録レスポンス"""

    cannot_send_reason_code: str | None = Field(None, description="送信不可理由コード")
    cannot_send_reason_name: str | None = Field(None, description="送信不可理由名")
    duration_minutes: int = Field(..., description="作業時間（分）")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "assignment_id": 2,
                "worker_id": 1,
                "status": "cannot_send",
                "started_at": "2025-11-22T11:00:00Z",
                "completed_at": "2025-11-22T11:15:00Z",
                "form_submission_result": None,
                "cannot_send_reason_id": 1,
                "cannot_send_reason_code": "FORM_NOT_FOUND",
                "cannot_send_reason_name": "フォームが見つからない",
                "duration_minutes": 15,
                "notes": "フォームが見つからず",
                "created_at": "2025-11-22T11:15:00Z",
                "updated_at": "2025-11-22T11:15:00Z",
                "deleted_at": None,
            }
        },
    )


# ========================================
# 統計情報レスポンス
# ========================================


class WorkRecordStatisticsResponse(BaseModel):
    """作業記録統計レスポンス"""

    total_records: int = Field(..., description="総作業記録数")
    sent_count: int = Field(..., description="送信済み件数")
    cannot_send_count: int = Field(..., description="送信不可件数")
    success_rate: float = Field(..., description="送信成功率（%）")
    average_duration_minutes: float = Field(..., description="平均作業時間（分）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_records": 100,
                "sent_count": 85,
                "cannot_send_count": 15,
                "success_rate": 85.0,
                "average_duration_minutes": 25.5,
            }
        },
    )
