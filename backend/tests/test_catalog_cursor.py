import base64

import pytest

from app.catalog_cursor import (
    CatalogCursorCodec,
    InvalidCatalogCursor,
    MAX_TOKEN_BYTES,
    TTL_SECONDS,
)


KEY = b"k" * 32
QUERY = "a" * 64


def test_cursor_round_trip_and_expiry_are_bound_to_issue_time():
    codec = CatalogCursorCodec(KEY)
    token = codec.encode({"providers": {"one": {"next_href": "https://hidden.example/?token=x"}}}, query_hash=QUERY, now=100)
    decoded = codec.decode(token, expected_query_hash=QUERY, now=100)
    assert decoded["providers"]["one"]["next_href"].startswith("https://")
    assert decoded["expires_at"] == 100 + TTL_SECONDS
    with pytest.raises(InvalidCatalogCursor):
        codec.decode(token, expected_query_hash=QUERY, now=100 + TTL_SECONDS)


def test_cursor_rejects_tampering_wrong_key_and_query_binding():
    token = CatalogCursorCodec(KEY).encode({"page": 2}, query_hash=QUERY, now=100)
    with pytest.raises(InvalidCatalogCursor):
        CatalogCursorCodec(KEY).decode(token[:-1] + ("A" if token[-1] != "A" else "B"), expected_query_hash=QUERY, now=100)
    with pytest.raises(InvalidCatalogCursor):
        CatalogCursorCodec(b"x" * 32).decode(token, expected_query_hash=QUERY, now=100)
    with pytest.raises(InvalidCatalogCursor):
        CatalogCursorCodec(KEY).decode(token, expected_query_hash="b" * 64, now=100)


@pytest.mark.parametrize("token", ["", "not a cursor", "!!!!", "A", "e30"])
def test_cursor_rejects_malformed_tokens(token):
    with pytest.raises(InvalidCatalogCursor):
        CatalogCursorCodec(KEY).decode(token, expected_query_hash=QUERY, now=100)


def test_cursor_rejects_oversized_token():
    with pytest.raises(InvalidCatalogCursor):
        CatalogCursorCodec(KEY).decode("A" * (MAX_TOKEN_BYTES + 1), expected_query_hash=QUERY, now=100)


def test_cursor_key_requires_exactly_32_bytes():
    with pytest.raises(ValueError):
        CatalogCursorCodec(b"short")


def test_cursor_key_from_environment_is_base64_and_server_side(monkeypatch):
    monkeypatch.setenv("SENTINEL_CURSOR_ENCRYPTION_KEY", base64.b64encode(KEY).decode("ascii"))
    assert CatalogCursorCodec.from_env().encode({}, query_hash=QUERY, now=1)
    monkeypatch.setenv("SENTINEL_CURSOR_ENCRYPTION_KEY", "invalid")
    with pytest.raises(ValueError):
        CatalogCursorCodec.from_env()
    monkeypatch.delenv("SENTINEL_CURSOR_ENCRYPTION_KEY")
    with pytest.raises(ValueError):
        CatalogCursorCodec.from_env()
