"""Authenticated encryption for opaque catalog pagination cursors."""

import base64
import binascii
import json
import os
import re
import time
from typing import Any, Mapping

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AAD = b"sentinel-explorer:catalog-cursor:v1"
NONCE_BYTES = 12
KEY_BYTES = 32
TTL_SECONDS = 15 * 60
MAX_TOKEN_BYTES = 64 * 1024
_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class InvalidCatalogCursor(ValueError):
    """Raised for malformed, expired, tampered or mismatched cursors."""


class CatalogCursorCodec:
    """Versioned AES-256-GCM cursor codec; keys are supplied by server config."""

    def __init__(self, key: bytes) -> None:
        if len(key) != KEY_BYTES:
            raise ValueError("catalog cursor key must be exactly 32 bytes")
        self._cipher = AESGCM(key)

    @classmethod
    def from_env(cls, name: str = "SENTINEL_CURSOR_ENCRYPTION_KEY") -> "CatalogCursorCodec":
        encoded = os.environ.get(name)
        if not encoded:
            raise ValueError("catalog cursor encryption key is not configured")
        try:
            key = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("catalog cursor encryption key is invalid") from exc
        return cls(key)

    def encode(
        self,
        state: Mapping[str, Any],
        *,
        query_hash: str,
        now: int | None = None,
    ) -> str:
        if not query_hash:
            raise ValueError("query_hash must not be empty")
        issued_at = int(time.time()) if now is None else int(now)
        payload = dict(state)
        payload.update(
            {
                "v": 1,
                "query_hash": query_hash,
                "expires_at": issued_at + TTL_SECONDS,
            }
        )
        plaintext = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        nonce = os.urandom(NONCE_BYTES)
        encrypted = nonce + self._cipher.encrypt(nonce, plaintext, AAD)
        token = base64.urlsafe_b64encode(encrypted).rstrip(b"=").decode("ascii")
        if len(token.encode("ascii")) > MAX_TOKEN_BYTES:
            raise InvalidCatalogCursor("cursor state exceeds the configured size limit")
        return token

    def decode(
        self,
        token: str,
        *,
        expected_query_hash: str,
        now: int | None = None,
    ) -> dict[str, Any]:
        if (
            not isinstance(token, str)
            or not token
            or len(token.encode("utf-8")) > MAX_TOKEN_BYTES
            or not _TOKEN_RE.fullmatch(token)
        ):
            raise InvalidCatalogCursor("invalid cursor")
        try:
            raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
            if base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != token:
                raise InvalidCatalogCursor("invalid cursor")
            if len(raw) <= NONCE_BYTES + 16:
                raise InvalidCatalogCursor("invalid cursor")
            plaintext = self._cipher.decrypt(raw[:NONCE_BYTES], raw[NONCE_BYTES:], AAD)
            payload = json.loads(plaintext)
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, InvalidTag, ValueError) as exc:
            if isinstance(exc, InvalidCatalogCursor):
                raise
            raise InvalidCatalogCursor("invalid cursor") from exc

        if not isinstance(payload, dict):
            raise InvalidCatalogCursor("invalid cursor")
        current = int(time.time()) if now is None else int(now)
        if (
            payload.get("v") != 1
            or payload.get("query_hash") != expected_query_hash
            or not isinstance(payload.get("expires_at"), int)
            or payload["expires_at"] <= current
        ):
            raise InvalidCatalogCursor("invalid cursor")
        return payload
