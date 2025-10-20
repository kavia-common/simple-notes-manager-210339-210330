# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-SEC-001
# User Story: As a system, I need to identify users and enforce RBAC for notes.
# Acceptance Criteria:
# - current_user dependency from headers (X-User-Id, X-User-Role)
# - RBAC check: admin, user; least privilege defaults
# - Public interfaces documented
# GxP Impact: YES - Access controls
# Risk Level: MEDIUM
# Validation Protocol: VP-SEC-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from typing import Literal, Optional
from fastapi import Header, HTTPException, status
from pydantic import BaseModel
# ============================================================================


class UserContext(BaseModel):
    """Represents the current request's user context."""
    user_id: Optional[str] = None
    role: Literal["admin", "user"] = "user"


# PUBLIC_INTERFACE
async def get_current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(default="user", alias="X-User-Role"),
) -> UserContext:
    """
    Return a stubbed current user context from headers.

    Defaults to role 'user' with no user_id if not provided.
    """
    role = "admin" if str(x_user_role).lower() == "admin" else "user"
    return UserContext(user_id=x_user_id, role=role)


# PUBLIC_INTERFACE
def require_role(user: UserContext, allowed: list[str]) -> None:
    """
    Enforce role-based access control.

    Parameters:
    - user: UserContext
    - allowed: list of allowed roles
    Raises HTTPException 403 if not allowed.
    """
    if user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this operation",
        )


# PUBLIC_INTERFACE
def user_can_access_note(user: UserContext, owner_id: Optional[str]) -> bool:
    """
    Determine if a user can access a note based on role and ownership.

    Admins can access all notes; users can access only their own.
    """
    if user.role == "admin":
        return True
    return owner_id is not None and user.user_id is not None and owner_id == user.user_id
