#!/usr/bin/env python3
"""Safely check the public STAC roots and collections used for Sentinel-2 discovery."""
from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Provider:
    provider_id: str
    endpoint: str
    hostname: str


# Fixed allowlist. Never accept arbitrary endpoints or credentials from CLI/config.
PROVIDERS: dict[str, Provider] = {
    "earth-search": Provider(
        "earth-search", "https://earth-search.aws.element84.com/v1/",
        "earth-search.aws.element84.com",
    ),
    "cdse": Provider(
        "cdse", "https://stac.dataspace.copernicus.eu/v1/",
        "stac.dataspace.copernicus.eu",
    ),
    "planetary-computer": Provider(
        "planetary-computer", "https://planetarycomputer.microsoft.com/api/stac/v1/",
        "planetarycomputer.microsoft.com",
    ),
}
USER_AGENT = "SentinelExplorer-STAC-checker/1.0"


class CheckError(Exception):
    def __init__(self, stage: str, error_class: str, http_status: int | None = None):
        super().__init__(error_class)
        self.stage = stage
        self.error_class = error_class
        self.http_status = http_status


def probe_dns(hostname: str) -> None:
    socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)


def probe_network(hostname: str, timeout: float) -> dict[str, str]:
    result = {"dns": "UNKNOWN", "tcp": "UNKNOWN", "tls": "UNKNOWN"}
    try:
        probe_dns(hostname)
        result["dns"] = "PASS"
    except socket.gaierror:
        result["dns"] = "FAIL"
        result["error_class"] = "DNSResolutionError"
        return result
    except OSError as exc:
        result["dns"] = "FAIL"
        result["error_class"] = type(exc).__name__
        return result

    try:
        # TCP and TLS are measured as separate states over the same connection.
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=timeout) as raw_socket:
            result["tcp"] = "PASS"
            try:
                with context.wrap_socket(raw_socket, server_hostname=hostname):
                    result["tls"] = "PASS"
            except (ssl.SSLError, OSError) as exc:
                result["tls"] = "FAIL"
                result["error_class"] = type(exc).__name__
    except OSError as exc:
        result["tcp"] = "FAIL"
        result["error_class"] = type(exc).__name__
    return result


class AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hostname: str):
        super().__init__()
        self.allowed_hostname = allowed_hostname

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        is_loopback_http = parsed.scheme == "http" and self.allowed_hostname in {"127.0.0.1", "::1", "localhost"}
        if (parsed.scheme != "https" and not is_loopback_http) or parsed.hostname != self.allowed_hostname:
            raise urllib.error.URLError("redirect blocked")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_json(url: str, hostname: str, timeout: float) -> tuple[int, Any, float]:
    parsed = urllib.parse.urlsplit(url)
    is_loopback_http = parsed.scheme == "http" and hostname in {"127.0.0.1", "::1", "localhost"}
    if (parsed.scheme != "https" and not is_loopback_http) or parsed.hostname != hostname or parsed.username or parsed.password:
        raise CheckError("CONFIG", "EndpointNotAllowlisted")
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json, application/geo+json", "User-Agent": USER_AGENT},
        method="GET",
    )
    opener = urllib.request.build_opener(AllowlistedRedirectHandler(hostname))
    started = time.monotonic()
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            body = response.read(2 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as exc:
        raise CheckError("HTTP", "HTTPError", exc.code) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", None)
        error_class = type(reason).__name__ if reason is not None else type(exc).__name__
        raise CheckError("HTTP", error_class) from None
    elapsed_ms = round((time.monotonic() - started) * 1000, 1)
    if len(body) > 2 * 1024 * 1024:
        raise CheckError("JSON", "ResponseTooLarge", status)
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise CheckError("JSON", "InvalidJSON", status) from None
    return status, payload, elapsed_ms


def check_provider(
    provider: Provider,
    timeout: float = 10.0,
    network_probe: Callable[[str, float], dict[str, str]] = probe_network,
    json_getter: Callable[[str, str, float], tuple[int, Any, float]] = get_json,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "provider": provider.provider_id,
        "hostname": provider.hostname,
        "dns": "UNKNOWN",
        "tcp": "UNKNOWN",
        "tls": "UNKNOWN",
        "root": "UNKNOWN",
        "collections": "UNKNOWN",
        "status": "FAIL",
    }
    network = network_probe(provider.hostname, timeout)
    result.update(network)
    if any(network.get(stage) != "PASS" for stage in ("dns", "tcp", "tls")):
        result["error_stage"] = "NETWORK"
        result["error_class"] = network.get("error_class", "NetworkCheckFailed")
        return result

    root_url = provider.endpoint.rstrip("/") + "/"
    collections_url = urllib.parse.urljoin(root_url, "collections")
    try:
        root_status, root_payload, root_ms = json_getter(root_url, provider.hostname, timeout)
        result["root_http_status"] = root_status
        result["root_latency_ms"] = root_ms
        if not isinstance(root_payload, dict) or not isinstance(root_payload.get("stac_version"), str) or not isinstance(root_payload.get("links"), list):
            raise CheckError("ROOT_SCHEMA", "InvalidSTACRoot", root_status)
        result["root"] = "PASS"

        collections_status, collections_payload, collections_ms = json_getter(collections_url, provider.hostname, timeout)
        result["collections_http_status"] = collections_status
        result["collections_latency_ms"] = collections_ms
        if not isinstance(collections_payload, dict) or not isinstance(collections_payload.get("collections"), list):
            raise CheckError("COLLECTIONS_SCHEMA", "InvalidCollectionsResponse", collections_status)
        result["collections_count"] = len(collections_payload["collections"])
        result["collections"] = "PASS"
        result["status"] = "PASS"
    except CheckError as exc:
        result["error_stage"] = exc.stage
        result["error_class"] = exc.error_class
        if exc.http_status is not None:
            result["error_http_status"] = exc.http_status
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check allowlisted public Sentinel-2 STAC catalogs.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--provider", choices=sorted(PROVIDERS))
    selection.add_argument("--all", action="store_true", help="check every configured provider")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-connection/request timeout in seconds (default: 10)")
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 60:
        parser.error("--timeout must be between 0.1 and 60 seconds")

    selected = list(PROVIDERS.values()) if args.all else [PROVIDERS[args.provider]]
    reports = [check_provider(provider, args.timeout) for provider in selected]
    print(json.dumps(reports if args.all else reports[0], ensure_ascii=False, indent=2))
    return 0 if all(report["status"] == "PASS" for report in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
