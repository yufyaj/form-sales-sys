"""
リスト項目割り当て関連のPydanticスキーマ定義

API境界でのバリデーションとデータ変換を行うDTOスキーマ
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ========================================
# リクエストスキーマ
# ========================================


class BulkAssignRequest(BaseModel):
    """リストへのワーカー一括割り当てリクエスト"""

    worker_id: int = Field(
        ...,
        gt=0,
        description="ワーカーID",
        examples=[123],
    )
    count: int = Field(
        ...,
        gt=0,
        le=1000,
        description="割り当て件数（最大1000件）",
        examples=[10],
    )


# ========================================
# レスポンススキーマ
# ========================================


class ListItemAssignmentResponse(BaseModel):
    """リスト項目割り当てレスポンス"""

    id: int = Field(..., description="割り当てID")
    list_item_id: int = Field(..., description="リスト項目ID")
    worker_id: int = Field(..., description="ワーカーID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "list_item_id": 100,
                "worker_id": 123,
                "created_at": "2025-11-22T10:00:00Z",
                "updated_at": "2025-11-22T10:00:00Z",
            }
        },
    )


class BulkAssignResponse(BaseModel):
    """リストへのワーカー一括割り当てレスポンス"""

    assigned_count: int = Field(
        ...,
        description="実際に割り当てられた件数",
        examples=[10],
    )
    assignments: list[ListItemAssignmentResponse] = Field(
        ...,
        description="作成された割り当てのリスト",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assigned_count": 2,
                "assignments": [
                    {
                        "id": 1,
                        "list_item_id": 100,
                        "worker_id": 123,
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-22T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "list_item_id": 101,
                        "worker_id": 123,
                        "created_at": "2025-11-22T10:00:00Z",
                        "updated_at": "2025-11-22T10:00:00Z",
                    },
                ],
            }
        },
    )
