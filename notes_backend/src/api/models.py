# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-MODEL-001
# User Story: As a system, I need structured models for notes and audit logs
#             to ensure data integrity and GxP-compliant audit trails.
# Acceptance Criteria:
# - Note model with title/content/created_at/updated_at/user_id
# - AuditLog model capturing before/after states with timestamps
# - SQLModel based with SQLite
# GxP Impact: YES - Data integrity and audit trail
# Risk Level: MEDIUM
# Validation Protocol: VP-MODEL-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON
# ============================================================================


class Note(SQLModel, table=True):
    """SQLModel Note table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True, description="Note title")
    content: str = Field(min_length=1, max_length=10_000, description="Note content")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[str] = Field(
        default=None, description="User identifier who owns the note"
    )


class AuditLog(SQLModel, table=True):
    """Audit trail entries for CRUD operations per GxP."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, description="User performing action")
    action: str = Field(description="Action type: CREATE/READ/UPDATE/DELETE/ERROR")
    entity: str = Field(description="Entity type e.g., Note")
    entity_id: Optional[int] = Field(default=None, description="Entity primary key")
    before_state: Optional[dict] = Field(
        default=None, sa_column=Column(JSON), description="State before change"
    )
    after_state: Optional[dict] = Field(
        default=None, sa_column=Column(JSON), description="State after change"
    )
    reason: Optional[str] = Field(default=None, description="Reason for change")
    error: Optional[str] = Field(default=None, description="Technical error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
