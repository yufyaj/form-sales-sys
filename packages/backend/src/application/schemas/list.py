"""
List schema definitions using Pydantic

DTO schemas for API request/response validation and data transformation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.entities.list_entity import ListStatus


# Base schema
class ListBase(BaseModel):
    """Base class for list schemas"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="List name (max 255 characters)",
        examples=["January 2025 Campaign Target Companies"],
    )
    description: str | None = Field(
        None,
        description="List description",
        examples=["List for new customer development"],
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize list name - remove control characters and normalize spaces"""
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("List name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """Sanitize description - remove control characters (allow tabs and newlines)"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


# Request schemas
class ListCreateRequest(ListBase):
    """List creation request"""

    organization_id: int = Field(
        ...,
        gt=0,
        description="Organization ID of sales support company",
    )


class ListUpdateRequest(BaseModel):
    """List update request"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="List name (max 255 characters)",
    )
    description: str | None = Field(
        None,
        description="List description",
    )

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Sanitize list name"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("List name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """Sanitize list description"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c in ["\n", "\t"])
        return cleaned if cleaned else None


class ListDuplicateRequest(BaseModel):
    """List duplication request"""

    new_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="New list name (if not specified, generates '{original_name} のコピー')",
    )

    @field_validator("new_name")
    @classmethod
    def sanitize_new_name(cls, v: str | None) -> str | None:
        """Sanitize new list name"""
        if v is None:
            return None
        cleaned = "".join(c for c in v if c.isprintable() or c.isspace())
        cleaned = " ".join(cleaned.split())
        if not cleaned:
            raise ValueError("List name cannot be empty")
        return cleaned


# Response schemas
class ListResponse(BaseModel):
    """List response"""

    id: int = Field(..., description="List ID")
    organization_id: int = Field(..., description="Organization ID of sales support company")
    name: str = Field(..., description="List name")
    description: str | None = Field(None, description="List description")
    status: ListStatus = Field(..., description="List status (draft/submitted/accepted/rejected)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    deleted_at: datetime | None = Field(None, description="Deletion timestamp (soft delete)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "organization_id": 10,
                "name": "January 2025 Campaign Target Companies",
                "description": "List for new customer development",
                "status": "draft",
                "created_at": "2025-11-03T10:00:00Z",
                "updated_at": "2025-11-10T15:30:00Z",
                "deleted_at": None,
            }
        },
    )


class ListListResponse(BaseModel):
    """List collection response"""

    lists: list[ListResponse] = Field(..., description="Array of lists")
    total: int = Field(..., description="Total count")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Page size")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lists": [
                    {
                        "id": 1,
                        "organization_id": 10,
                        "name": "January 2025 Campaign Target Companies",
                        "description": "List for new customer development",
                        "status": "draft",
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
