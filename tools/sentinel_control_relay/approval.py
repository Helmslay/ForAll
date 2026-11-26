"""Create an opaque, hash-bound Sentinel command approval attestation.

The public ForAll workflow receives only hashes and a fresh tag. For automated
Issue-event runs, the only trigger data is a public relay Issue created by the
trusted operator; its body contains no private Issue identifiers or command
arguments.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Any

REPOSITORY = "Helmslay/ForAll"
REPOSITORY_ID = "1461236096"
WORKFLOW_PATH = ".github/workflows/sentinel-control-command-approval.yml"
WORKFLOW_REF = f"{REPOSITORY}/{WORKFLOW_PATH}@refs/heads/main"
ALLOWED_ACTOR = "Helmslay"
ALLOWED_ACTOR_ID = 151124217
PUBLIC_ISSUE_TITLE_PREFIX = "Sentinel command relay "
RELEASE_TAG_RE = re.compile(r"sentinel-command-[0-9a-f]{32}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA40_RE = re.compile(r"[0-9a-f]{40}\Z")
MAX_EVENT_BYTES = 64 * 1024
MAX_PUBLIC_ISSUE_BODY_BYTES = 4096
ISSUE_BODY_FIELDS = {
    "request_sha256", "title_sha256", "issue_binding_sha256",
    "release_tag", "confirmation",
}


class ApprovalInputError(ValueError):
    """Raised when workflow context or approval input is not trusted."""


def _positive_int(value: str, field: str, *, maximum: int = 2**63 - 1) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]{0,18}", value):
        raise ApprovalInputError(field + "_invalid")
    parsed = int(value)
    if parsed > maximum:
        raise ApprovalInputError(field + "_invalid")
    return parsed


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ApprovalInputError("duplicate_json_key")
        result[key] = value
    return result


def _issue_event_inputs(env: Mapping[str, str]) -> dict[str, str]:
    event_path = env.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        raise ApprovalInputError("issue_event_path_missing")
    path = Path(event_path)
    try:
        info = path.stat()
        if not path.is_file() or info.st_size > MAX_EVENT_BYTES:
            raise ApprovalInputError("issue_event_invalid")
        event = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except ApprovalInputError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise ApprovalInputError("issue_event_invalid") from None

    if not isinstance(event, dict):
        raise ApprovalInputError("issue_event_invalid")
    issue = event.get("issue")
    sender = event.get("sender")
    repository = event.get("repository")
    if (
        event.get("action") != "opened"
        or not isinstance(issue, dict)
        or "pull_request" in issue
        or issue.get("state") != "open"
        or not isinstance(issue.get("title"), str)
        or not isinstance(issue.get("body"), str)
        or len(issue["body"].encode("utf-8")) > MAX_PUBLIC_ISSUE_BODY_BYTES
        or not isinstance(issue.get("user"), dict)
        or issue["user"].get("id") != ALLOWED_ACTOR_ID
        or not isinstance(sender, dict)
        or sender.get("id") != ALLOWED_ACTOR_ID
        or not isinstance(repository, dict)
        or repository.get("id") != int(REPOSITORY_ID)
        or repository.get("full_name") != REPOSITORY
    ):
        raise ApprovalInputError("issue_event_identity_mismatch")

    try:
        payload = json.loads(
            issue["body"],
            object_pairs_hook=_unique_object,
        )
    except ApprovalInputError:
        raise
    except (json.JSONDecodeError, RecursionError):
        raise ApprovalInputError("issue_payload_invalid") from None
    if (
        not isinstance(payload, dict)
        or set(payload) != ISSUE_BODY_FIELDS
        or any(not isinstance(payload.get(key), str) for key in ISSUE_BODY_FIELDS)
    ):
        raise ApprovalInputError("issue_payload_schema_invalid")

    release_tag = payload["release_tag"]
    expected_title = PUBLIC_ISSUE_TITLE_PREFIX + release_tag
    if issue["title"] != expected_title:
        raise ApprovalInputError("issue_title_mismatch")
    if payload["confirmation"] != "I_APPROVE":
        raise ApprovalInputError("explicit_confirmation_missing")
    return payload


def _approval_inputs(env: Mapping[str, str]) -> dict[str, str]:
    event_name = env.get("GITHUB_EVENT_NAME")
    if event_name == "workflow_dispatch":
        return {
            "request_sha256": env.get("REQUEST_SHA256", ""),
            "title_sha256": env.get("TITLE_SHA256", ""),
            "issue_binding_sha256": env.get("ISSUE_BINDING_SHA256", ""),
            "release_tag": env.get("RELEASE_TAG", ""),
            "confirmation": env.get("CONFIRMATION", ""),
        }
    if event_name == "issues":
        return _issue_event_inputs(env)
    raise ApprovalInputError("github_event_name_mismatch")


def build_attestation(env: Mapping[str, str]) -> dict[str, Any]:
    """Validate the immutable GitHub workflow context and build the attestation."""
    expected = {
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REPOSITORY_ID": REPOSITORY_ID,
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
        "GITHUB_WORKFLOW": "Sentinel Control Command Approval",
        "GITHUB_ACTOR": ALLOWED_ACTOR,
        "GITHUB_ACTOR_ID": str(ALLOWED_ACTOR_ID),
    }
    for key, value in expected.items():
        if env.get(key) != value:
            raise ApprovalInputError(key.lower() + "_mismatch")

    inputs = _approval_inputs(env)
    request_sha = inputs["request_sha256"]
    title_sha = inputs["title_sha256"]
    issue_binding_sha = inputs["issue_binding_sha256"]
    release_tag = inputs["release_tag"]
    if not SHA256_RE.fullmatch(request_sha):
        raise ApprovalInputError("request_sha256_invalid")
    if not SHA256_RE.fullmatch(title_sha):
        raise ApprovalInputError("title_sha256_invalid")
    if not SHA256_RE.fullmatch(issue_binding_sha):
        raise ApprovalInputError("issue_binding_sha256_invalid")
    if not RELEASE_TAG_RE.fullmatch(release_tag):
        raise ApprovalInputError("release_tag_invalid")
    if inputs["confirmation"] != "I_APPROVE":
        raise ApprovalInputError("explicit_confirmation_missing")

    workflow_sha = env.get("GITHUB_SHA", "")
    if not SHA40_RE.fullmatch(workflow_sha):
        raise ApprovalInputError("workflow_sha_invalid")

    run_id = _positive_int(env.get("GITHUB_RUN_ID", ""), "workflow_run_id")
    run_attempt = _positive_int(env.get("GITHUB_RUN_ATTEMPT", ""), "workflow_run_attempt", maximum=999999)
    approved_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    return {
        "schema_version": 1,
        "status": "approved",
        "repository": REPOSITORY,
        "repository_id": int(REPOSITORY_ID),
        "workflow_path": WORKFLOW_PATH,
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "workflow_sha": workflow_sha,
        "workflow_actor": ALLOWED_ACTOR,
        "workflow_actor_id": ALLOWED_ACTOR_ID,
        "request_sha256": request_sha,
        "title_sha256": title_sha,
        "issue_binding_sha256": issue_binding_sha,
        "release_tag": release_tag,
        "approved_at_utc": approved_at,
        "approval_id": str(uuid.uuid4()),
    }


def write_attestation(value: Mapping[str, Any], output: Path) -> None:
    """Write a small deterministic JSON file with owner-only permissions."""
    if not isinstance(output, Path) or not output.is_absolute():
        raise ApprovalInputError("output_path_invalid")
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    try:
        temporary.write_text(raw, encoding="utf-8", newline="\n")
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        os.replace(temporary, output)
        try:
            os.chmod(output, 0o600)
        except OSError:
            pass
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a hash-only Sentinel command approval attestation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="validate workflow context and write one attestation")
    create.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        value = build_attestation(os.environ)
        write_attestation(value, args.output.resolve())
    except (ApprovalInputError, OSError, TypeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, ApprovalInputError) else "attestation_write_failed"
        print("sentinel_relay_error=" + code, file=__import__("sys").stderr)
        return 2
    print("sentinel_relay_attestation=created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
