# ============================================================================
# REQUIREMENT TRACEABILITY
# ============================================================================
# Requirement ID: REQ-API-DB-001
# User Story: As a developer, I need a lightweight persistent database with
#             proper session management to store notes and audit logs.
# Acceptance Criteria:
# - SQLite database with SQLModel
# - Session dependency factory
# - Create tables on startup
# GxP Impact: YES - Data persistence and integrity
# Risk Level: LOW
# Validation Protocol: VP-DB-001
# ============================================================================

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================
from contextlib import contextmanager
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
import logging
# ============================================================================

# Configure module logger
logger = logging.getLogger(__name__)

# SQLite file DB for persistence; no env var dependencies per requirements.
SQLITE_URL = "sqlite:///./app.db"

# Create engine with reasonable pragmas for SQLite
engine = create_engine(
    SQLITE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This is intended to be called at application startup to ensure tables exist.
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized and tables created.")
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        raise


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager for a database session with commit/rollback semantics.
    Ensures transaction safety for GxP compliance.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# PUBLIC_INTERFACE
def get_session() -> Generator[Session, None, None]:
    """Provide a FastAPI dependency that yields a SQLModel Session."""
    with session_scope() as session:
        yield session
