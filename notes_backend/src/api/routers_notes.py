# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-NOTES-API-001
# User Story: As a user, I want to create, list, retrieve, update, and delete notes.
# Acceptance Criteria:
# - Endpoints: POST /notes, GET /notes, GET /notes/{id}, PUT /notes/{id}, DELETE /notes/{id}
# - Validation, RBAC, and audit logging
# - Pagination with limit/offset and sort by created_at desc
# GxP Impact: YES
# Risk Level: HIGH
# Validation Protocol: VP-NOTES-API-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from ..db import get_session
from ..models import Note
from ..schemas import NoteCreate, NoteUpdate, NoteOut, PaginatedNotes
from ..security import get_current_user, UserContext, require_role, user_can_access_note
from ..audit import write_audit_entry
# ============================================================================


router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={404: {"description": "Not found"}},
)


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Create a new note. Requires role user or admin. Owner set from X-User-Id.",
)
def create_note(
    payload: NoteCreate,
    session: Session = Depends(get_session),
    user: UserContext = Depends(get_current_user),
):
    """Create a new note, with audit log entry for CREATE."""
    # RBAC: allow both admin and user
    require_role(user, ["admin", "user"])
    note = Note(title=payload.title, content=payload.content, owner_id=user.user_id)
    session.add(note)
    session.flush()  # to get note.id
    write_audit_entry(
        session,
        user=user,
        action="CREATE",
        entity="Note",
        entity_id=note.id,
        before_state=None,
        after_state=note.model_dump(),
        reason=payload.reason,
    )
    return NoteOut(**note.model_dump())


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=PaginatedNotes,
    summary="List notes",
    description="List notes with pagination and sorting by created_at desc. Users see only their own; admins see all.",
)
def list_notes(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
    user: UserContext = Depends(get_current_user),
):
    """List notes with RBAC scoping."""
    # RBAC: allow both admin and user
    require_role(user, ["admin", "user"])

    statement = select(Note)
    if user.role != "admin":
        statement = statement.where(Note.owner_id == user.user_id)
    total = session.exec(statement).count()  # SQLModel returns RowSet; convert to list for count
    # Re-execute with pagination and sort
    items: List[Note] = list(
        session.exec(
            statement.order_by(Note.created_at.desc()).offset(offset).limit(limit)
        )
    )
    return PaginatedNotes(
        items=[NoteOut(**n.model_dump()) for n in items],
        total=total,
        limit=limit,
        offset=offset,
    )


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get note by ID",
    description="Retrieve a single note. Users can only access their own; admins can access all.",
)
def get_note(
    note_id: int,
    session: Session = Depends(get_session),
    user: UserContext = Depends(get_current_user),
):
    """Retrieve note with access control."""
    require_role(user, ["admin", "user"])
    note = session.get(Note, note_id)
    if not note or not user_can_access_note(user, note.owner_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut(**note.model_dump())


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update note fields; requires access to the note. Audit logs capture before/after.",
)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    session: Session = Depends(get_session),
    user: UserContext = Depends(get_current_user),
):
    """Update a note with audit logging and validation."""
    require_role(user, ["admin", "user"])
    note = session.get(Note, note_id)
    if not note or not user_can_access_note(user, note.owner_id):
        raise HTTPException(status_code=404, detail="Note not found")
    before = note.model_dump()
    updated = False
    if payload.title is not None:
        note.title = payload.title
        updated = True
    if payload.content is not None:
        note.content = payload.content
        updated = True
    if not updated:
        # Nothing to update -> validation style error
        raise HTTPException(status_code=400, detail="No fields provided to update")
    from datetime import datetime as _dt

    note.updated_at = _dt.utcnow()
    session.add(note)
    session.flush()
    write_audit_entry(
        session,
        user=user,
        action="UPDATE",
        entity="Note",
        entity_id=note.id,
        before_state=before,
        after_state=note.model_dump(),
        reason=payload.reason,
    )
    return NoteOut(**note.model_dump())


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note; requires access. Audit logs include before state.",
)
def delete_note(
    note_id: int,
    reason: Optional[str] = Query(default=None, description="Reason for deletion"),
    session: Session = Depends(get_session),
    user: UserContext = Depends(get_current_user),
):
    """Delete a note with audit logging."""
    require_role(user, ["admin", "user"])
    note = session.get(Note, note_id)
    if not note or not user_can_access_note(user, note.owner_id):
        raise HTTPException(status_code=404, detail="Note not found")
    before = note.model_dump()
    session.delete(note)
    session.flush()
    write_audit_entry(
        session,
        user=user,
        action="DELETE",
        entity="Note",
        entity_id=note_id,
        before_state=before,
        after_state=None,
        reason=reason,
    )
    return
