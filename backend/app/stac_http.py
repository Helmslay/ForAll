"""Safe asynchronous HTTP transport for configured STAC endpoints."""

import asyncio
import json
import logging
from collections.abc import Collection, Mapping
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.catalog_provider import (
    CatalogConfigurationError,
    CatalogProviderError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)

logger = logging.getLogger(__name__)

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class StacHttpClient:
    """HTTP JSON client restricted to explicitly allowlisted HTTPS hosts."""

    def __init__(
        self,
        *,
        provider_id: str,
        allowed_hosts: Collection[str],
        timeout_seconds: float = 15.0,
        max_retries: int = 2,
        max_response_bytes: int = 2_000_000,
        retry_backoff_seconds: float = 0.25,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not provider_id.strip():
            raise ValueError("provider_id must not be empty")
        hosts = frozenset(host.strip().lower() for host in allowed_hosts if host.strip())
        if not hosts:
            raise CatalogConfigurationError(provider_id)
        if (
            timeout_seconds <= 0
            or max_retries < 0
            or max_retries > 5
            or max_response_bytes <= 0
        ):
            raise ValueError("invalid STAC HTTP client limits")
        if retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds must not be negative")

        self.provider_id = provider_id
        self.allowed_hosts = hosts
        self.max_retries = max_retries
        self.max_response_bytes = max_response_bytes
        self.retry_backoff_seconds = retry_backoff_seconds
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
            transport=transport,
        )

    async def __aenter__(self) -> "StacHttpClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _validate_url(self, url: str) -> None:
        try:
            parsed = urlsplit(url)
            hostname = (parsed.hostname or "").lower()
            port = parsed.port
        except ValueError as exc:
            raise CatalogConfigurationError(self.provider_id) from exc

        if (
            parsed.scheme != "https"
            or hostname not in self.allowed_hosts
            or port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise CatalogConfigurationError(self.provider_id)

    async def request_json(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str | int | float] | None = None,
        json_body: Mapping[str, Any] | None = None,
    ) -> Any:
        """Request JSON without exposing upstream URLs or response bodies in logs."""
        normalized_method = method.upper()
        if normalized_method not in {"GET", "POST"}:
            raise CatalogConfigurationError(self.provider_id)
        self._validate_url(url)

        for attempt in range(self.max_retries + 1):
            try:
                async with self._client.stream(
                    normalized_method,
                    url,
                    params=params,
                    json=json_body,
                    headers={"Accept": "application/json, application/geo+json"},
                ) as response:
                    if response.status_code in _RETRYABLE_STATUSES:
                        if attempt < self.max_retries:
                            await asyncio.sleep(self._retry_delay(response, attempt))
                            continue
                        if response.status_code == 429:
                            raise CatalogRateLimitedError(self.provider_id)
                        raise CatalogUnavailableError(self.provider_id)

                    if not 200 <= response.status_code < 300:
                        raise CatalogProviderError(self.provider_id)

                    content_type = response.headers.get("content-type", "").lower()
                    media_type = content_type.split(";", 1)[0].strip()
                    if not (
                        media_type == "application/json"
                        or media_type.endswith("+json")
                    ):
                        raise CatalogProviderError(self.provider_id)

                    content_length = response.headers.get("content-length")
                    if content_length is not None:
                        try:
                            if int(content_length) > self.max_response_bytes:
                                raise CatalogProviderError(self.provider_id)
                        except ValueError as exc:
                            raise CatalogProviderError(self.provider_id) from exc

                    chunks: list[bytes] = []
                    total = 0
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > self.max_response_bytes:
                            raise CatalogProviderError(self.provider_id)
                        chunks.append(chunk)

                    try:
                        payload = json.loads(b"".join(chunks))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise CatalogProviderError(self.provider_id) from exc
                    if not isinstance(payload, dict):
                        raise CatalogProviderError(self.provider_id)
                    return payload

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                logger.warning(
                    "STAC transport attempt failed",
                    extra={
                        "provider_id": self.provider_id,
                        "attempt": attempt + 1,
                        "error_type": type(exc).__name__,
                    },
                )
                if attempt >= self.max_retries:
                    raise CatalogUnavailableError(self.provider_id) from exc
                await asyncio.sleep(self._backoff(attempt))

        raise CatalogUnavailableError(self.provider_id)

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return min(max(float(retry_after), 0.0), 1.0)
            except ValueError:
                pass
        return self._backoff(attempt)

    def _backoff(self, attempt: int) -> float:
        return min(self.retry_backoff_seconds * (2**attempt), 1.0)
