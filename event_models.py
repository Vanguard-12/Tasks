from __future__ import annotations

from typing import Literal, Union, Annotated

from pydantic import BaseModel, Field


class HttpOkEvent(BaseModel):
    """Successful HTTP request event."""

    kind: Literal["ok"] = Field(default="ok", description="Discriminator for a successful request")
    status: Literal[200] = Field(..., description="HTTP status code (always 200 for ok events)")
    path: str = Field(..., description="Requested path, e.g. /api/users")
    duration_ms: int = Field(..., description="Request duration in milliseconds")

    model_config = {
        "json_schema_extra": {"examples": [{"kind": "ok", "status": 200, "path": "/api/users", "duration_ms": 123}]}
    }


class HttpErrorEvent(BaseModel):
    """Error HTTP request event (4xx or 5xx)."""

    kind: Literal["error"] = Field(default="error", description="Discriminator for an error request")
    status: int = Field(..., ge=400, le=599, description="HTTP error status code (4xx or 5xx)")
    path: str = Field(..., description="Requested path that caused the error")
    error_message: str = Field(..., description="Human‑readable error description")

    model_config = {
        "json_schema_extra": {"examples": [{"kind": "error", "status": 404, "path": "/api/unknown", "error_message": "Not Found"}]}
    }


# Discriminated union – the ``kind`` field decides which model to use.
ApiEvent = Annotated[Union[HttpOkEvent, HttpErrorEvent], Field(discriminator="kind")]
