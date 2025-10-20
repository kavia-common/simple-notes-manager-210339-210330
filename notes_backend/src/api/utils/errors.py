# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-ERR-001
# User Story: As a client, I need consistent error responses; as a system, I need
#             technical logs for diagnostics while meeting GxP.
# Acceptance Criteria:
# - HTTPException handlers for structured output
# - Validation error normalization
# - Generic exception handler writing audit error entries (via router)
# GxP Impact: YES - Error handling
# Risk Level: MEDIUM
# Validation Protocol: VP-ERR-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
# ============================================================================

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return structured HTTP errors."""
    logger.warning("HTTP error: %s %s - %s", request.method, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": "HTTP_ERROR"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize validation errors into a stable structure."""
    logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": exc.errors(), "code": "VALIDATION_ERROR"},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch all handler for unexpected errors."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": "INTERNAL_SERVER_ERROR"},
    )
