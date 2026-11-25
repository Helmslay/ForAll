from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.sentinel_control_relay.approval import (
    ALLOWED_ACTOR,
    ALLOWED_ACTOR_ID,
    REPOSITORY,
    WORKFLOW_PATH,
    ApprovalInputError,
    build_attestation,
    write_attestation,
)

VALID_ENV = {
    "GITHUB_REPOSITORY": REPOSITORY,
    "GITHUB_REPOSITORY_ID": "1461236096",
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_WORKFLOW_REF": f"{REPOSITORY}/{WORKFLOW_PATH}@refs/heads/main",
    "GITHUB_WORKFLOW": "Sentinel Control Command Approval",
    "GITHUB_EVENT_NAME": "workflow_dispatch",
    "GITHUB_ACTOR": ALLOWED_ACTOR,
    "GITHUB_ACTOR_ID": ALLOWED_ACTOR_ID,
    "CONFIRMATION": "I_APPROVE",
    "REQUEST_SHA256": "a" * 64,
    "TITLE_SHA256": "b" * 64,
    "RELEASE_TAG": "sentinel-command-" + "c" * 32,
    "GITHUB_SHA": "d" * 40,
    "GITHUB_RUN_ID": "123456789",
    "GITHUB_RUN_ATTEMPT": "1",
}


class CommandApprovalAttestationTests(unittest.TestCase):
    def test_builds_exact_hash_only_schema(self):
        value = build_attestation(VALID_ENV)
        self.assertEqual(
            set(value),
            {
                "schema_version", "status", "repository", "repository_id",
                "workflow_path", "workflow_run_id", "workflow_run_attempt",
                "workflow_sha", "workflow_actor", "workflow_actor_id",
                "request_sha256", "title_sha256", "release_tag",
                "approved_at_utc", "approval_id",
            },
        )
        self.assertEqual(value["request_sha256"], "a" * 64)
        self.assertEqual(value["title_sha256"], "b" * 64)
        self.assertEqual(value["workflow_run_id"], 123456789)
        self.assertEqual(value["workflow_run_attempt"], 1)
        self.assertEqual(value["workflow_actor_id"], 151124217)
        self.assertNotIn("issue_body", value)
        self.assertNotIn("arguments", value)
        self.assertNotIn("private_key", value)

    def test_refuses_wrong_repository_ref_event_or_actor(self):
        for key, value in (
            ("GITHUB_REPOSITORY", "attacker/repo"),
            ("GITHUB_REF", "refs/heads/feature"),
            ("GITHUB_EVENT_NAME", "pull_request"),
            ("GITHUB_ACTOR", "someone-else"),
            ("GITHUB_ACTOR_ID", "42"),
            ("GITHUB_WORKFLOW_REF", "attacker/repo/workflow.yml@refs/heads/main"),
            ("CONFIRMATION", "CANCEL"),
        ):
            env = dict(VALID_ENV)
            env[key] = value
            with self.subTest(key=key), self.assertRaises(ApprovalInputError):
                build_attestation(env)

    def test_refuses_invalid_hashes_tags_and_run_identity(self):
        for key, value in (
            ("REQUEST_SHA256", "not-a-hash"),
            ("TITLE_SHA256", "f" * 63),
            ("RELEASE_TAG", "sentinel-command-" + "G" * 32),
            ("GITHUB_SHA", "e" * 39),
            ("GITHUB_RUN_ID", "0"),
            ("GITHUB_RUN_ATTEMPT", "0"),
        ):
            env = dict(VALID_ENV)
            env[key] = value
            with self.subTest(key=key), self.assertRaises(ApprovalInputError):
                build_attestation(env)

    def test_writes_deterministic_schema_without_request_payload(self):
        value = build_attestation(VALID_ENV)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "approval-attestation.json"
            write_attestation(value, output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written, value)
            self.assertNotIn("sentinel-explorer-agent.service", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
