from __future__ import annotations

from typing import Literal, Annotated, Union

from pydantic import BaseModel, Field


class HttpOkEvent(BaseModel):
    """Successful HTTP request event."""

    kind: Literal["ok"] = Field(
        "ok",
        description="Discriminator value indicating a successful request",
    )
    status: Literal[200] = Field(
        200,
        description="HTTP status code – always 200 for successful events",
    )
    path: str = Field(..., description="Requested endpoint path, e.g. /api/users")
    duration_ms: int = Field(..., description="Request duration in milliseconds")


class HttpErrorEvent(BaseModel):
    """Failed HTTP request event (4xx or 5xx)."""

    kind: Literal["error"] = Field(
        "error",
        description="Discriminator value indicating an error request",
    )
    status: int = Field(..., description="HTTP error status code (e.g., 404, 500)")
    path: str = Field(..., description="Requested endpoint path, e.g. /api/users")
    error_message: str = Field(..., description="Human‑readable error description")


# Discriminated union for all API events
ApiEvent = Annotated[Union[HttpOkEvent, HttpErrorEvent], Field(discriminator="kind")]
