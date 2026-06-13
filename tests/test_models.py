import pytest
from pydantic import ValidationError

from models import HttpOkEvent, HttpErrorEvent, ApiEvent


def test_ok_event_validation():
    data = {
        "kind": "ok",
        "status": 200,
        "path": "/api/users",
        "duration_ms": 150,
    }
    ev = HttpOkEvent(**data)
    assert ev.kind == "ok"
    assert ev.status == 200
    assert ev.path == "/api/users"
    assert ev.duration_ms == 150


def test_error_event_validation():
    data = {
        "kind": "error",
        "status": 404,
        "path": "/api/orders",
        "error_message": "Not found",
    }
    ev = HttpErrorEvent(**data)
    assert ev.kind == "error"
    assert ev.status == 404
    assert ev.path == "/api/orders"
    assert ev.error_message == "Not found"


def test_union_discriminator_ok():
    payload = {
        "kind": "ok",
        "status": 200,
        "path": "/api/users",
        "duration_ms": 123,
    }
    ev: ApiEvent = ApiEvent.validate(payload)  # type: ignore[attr-defined]
    assert isinstance(ev, HttpOkEvent)


def test_union_discriminator_error():
    payload = {
        "kind": "error",
        "status": 500,
        "path": "/api/payments",
        "error_message": "Server error",
    }
    ev: ApiEvent = ApiEvent.validate(payload)  # type: ignore[attr-defined]
    assert isinstance(ev, HttpErrorEvent)


def test_invalid_status_for_ok():
    # status other than 200 should raise a validation error for the OK branch
    data = {
        "kind": "ok",
        "status": 201,
        "path": "/api/users",
        "duration_ms": 100,
    }
    with pytest.raises(ValidationError):
        HttpOkEvent(**data)
