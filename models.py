from __future__ import annotations

from typing import Literal, Union, Annotated

from pydantic import BaseModel, Field


class HttpOkEvent(BaseModel):
    """Model for successful HTTP requests (status 200)."""

    kind: Literal["ok"] = Field(
        "ok",
        description="Discriminator value indicating a successful HTTP event",
    )
    status: Literal[200] = Field(
        200,
        description="HTTP status code – always 200 for this event type",
    )
    path: str = Field(..., description="Requested endpoint path, e.g. /api/users")
    duration_ms: int = Field(..., description="Request duration in milliseconds")


class HttpErrorEvent(BaseModel):
    """Model for error HTTP requests (4xx or 5xx)."""

    kind: Literal["error"] = Field(
        "error",
        description="Discriminator value indicating an error HTTP event",
    )
    status: int = Field(..., description="HTTP error status code (e.g., 404, 500)")
    path: str = Field(..., description="Requested endpoint path, e.g. /api/users")
    error_message: str = Field(..., description="Human‑readable error description")


# Discriminated union – the "kind" field tells Pydantic which model to use.
ApiEvent = Annotated[Union[HttpOkEvent, HttpErrorEvent], Field(discriminator="kind")]
