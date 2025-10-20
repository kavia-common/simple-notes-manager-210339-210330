# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-AUDIT-001
# User Story: As a system, I must record an audit trail for note CRUD operations.
# Acceptance Criteria:
# - Persist AuditLog on CREATE/UPDATE/DELETE and on ERROR
# - Include user_id, action, entity, entity_id, before/after, reason, timestamp
# GxP Impact: YES - Audit trail
# Risk Level: HIGH
# Validation Protocol: VP-AUDIT-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from typing import Optional, Any, Dict
from sqlmodel import Session
from .models import AuditLog
from .security import UserContext
import logging
# ============================================================================

logger = logging.getLogger(__name__)

# PUBLIC_INTERFACE
def write_audit_entry(
    session: Session,
    *,
    user: Optional[UserContext],
    action: str,
    entity: str,
    entity_id: Optional[int] = None,
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    error: Optional[str] = None,
) -> AuditLog:
    """Persist an audit log entry to the database."""
    entry = AuditLog(
        user_id=user.user_id if user else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
        reason=reason,
        error=error,
    )
    session.add(entry)
    # committed by caller's transaction
    logger.info(
        "Audit: action=%s entity=%s id=%s user=%s reason=%s",
        action,
        entity,
        entity_id,
        user.user_id if user else None,
        reason,
    )
    return entry
