# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-SCHEMA-001
# User Story: As a client, I need typed request/response schemas for notes API
#             with validation to ensure accurate data entry.
# Acceptance Criteria:
# - Create/Update input schemas with constraints
# - Response schemas with metadata fields
# - Pagination response support
# GxP Impact: YES - Validation controls
# Risk Level: LOW
# Validation Protocol: VP-SCHEMA-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
# ============================================================================


class ErrorResponse(BaseModel):
    """Standardized error response structure."""
    detail: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Stable error code for programmatic handling")


class NoteBase(BaseModel):
    """Shared fields for notes."""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, max_length=10_000, description="Note content")

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be blank")
        return v.strip()

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content must not be blank")
        return v


class NoteCreate(NoteBase):
    """Create note request."""
    reason: Optional[str] = Field(default=None, description="Reason for creation (optional)")


class NoteUpdate(BaseModel):
    """Update note request."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, min_length=1, max_length=10_000)
    reason: Optional[str] = Field(default=None, description="Reason for change")

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title must not be blank")
        return v.strip() if v is not None else v

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Content must not be blank")
        return v


class NoteOut(NoteBase):
    """Note response."""
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: Optional[str] = None


class PaginatedNotes(BaseModel):
    """Paginated list of notes."""
    items: List[NoteOut]
    total: int
    limit: int
    offset: int
