# Notes Backend

GxP-compliant Notes CRUD API using FastAPI + SQLModel + SQLite.

Run:
- uvicorn src.api.main:app --host 0.0.0.0 --port 3001

Endpoints:
- POST /notes
- GET /notes
- GET /notes/{id}
- PUT /notes/{id}
- DELETE /notes/{id}

Headers:
- X-User-Id: user identifier (optional, but used for ownership)
- X-User-Role: admin or user (default user)

Audit Trail:
- Captured for CREATE/UPDATE/DELETE with before/after states and reason.

Error Handling:
- Structured errors with code fields.
