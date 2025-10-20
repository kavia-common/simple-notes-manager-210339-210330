# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-APP-001
# User Story: As an operator, I need a FastAPI app exposing a GxP-compliant
#             Notes CRUD API with audit trails and RBAC.
# Acceptance Criteria:
# - App boots on port 3001 (handled by runner) without runtime errors
# - Includes notes router and exception handlers
# - Initializes SQLite/SQLModel database
# GxP Impact: YES
# Risk Level: HIGH
# Validation Protocol: VP-APP-001
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .db import init_db
from .utils import errors as error_utils
from .routers_notes import router as notes_router

# Initialize app with metadata for OpenAPI
app = FastAPI(
    title="Notes Management API",
    description="GxP-compliant Notes CRUD API with audit trail and RBAC.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health checks"},
        {"name": "Notes", "description": "Notes CRUD operations"},
    ],
)

# CORS policy - permissive for preview; can be tightened later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database and resources."""
    init_db()


@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy"}


# Register notes router
app.include_router(notes_router)


# Exception handlers
app.add_exception_handler(Exception, error_utils.unhandled_exception_handler)
app.add_exception_handler(
    error_utils.StarletteHTTPException, error_utils.http_exception_handler
)
app.add_exception_handler(
    error_utils.RequestValidationError, error_utils.validation_exception_handler
)


def custom_openapi():
    """Attach OpenAPI customization if needed."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
