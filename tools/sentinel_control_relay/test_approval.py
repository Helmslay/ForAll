from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sentinel_control_relay.approval import (
    ALLOWED_ACTOR,
    ALLOWED_ACTOR_ID,
    REPOSITORY,
    REPOSITORY_ID,
    WORKFLOW_PATH,
    ApprovalInputError,
    build_attestation,
    write_attestation,
)

VALID_ENV = {
    "GITHUB_REPOSITORY": REPOSITORY,
    "GITHUB_REPOSITORY_ID": REPOSITORY_ID,
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_WORKFLOW_REF": f"{REPOSITORY}/{WORKFLOW_PATH}@refs/heads/main",
    "GITHUB_WORKFLOW": "Sentinel Control Command Approval",
    "GITHUB_EVENT_NAME": "workflow_dispatch",
    "GITHUB_ACTOR": ALLOWED_ACTOR,
    "GITHUB_ACTOR_ID": str(ALLOWED_ACTOR_ID),
    "CONFIRMATION": "I_APPROVE",
    "REQUEST_SHA256": "a" * 64,
    "TITLE_SHA256": "b" * 64,
    "ISSUE_BINDING_SHA256": "e" * 64,
    "RELEASE_TAG": "sentinel-command-" + "c" * 32,
    "GITHUB_SHA": "d" * 40,
    "GITHUB_RUN_ID": "123456789",
    "GITHUB_RUN_ATTEMPT": "1",
}


class CommandApprovalAttestationTests(unittest.TestCase):
    def test_builds_exact_hash_only_schema_for_manual_compatibility(self):
        value = build_attestation(VALID_ENV)
        self.assertEqual(
            set(value),
            {
                "schema_version", "status", "repository", "repository_id",
                "workflow_path", "workflow_run_id", "workflow_run_attempt",
                "workflow_sha", "workflow_actor", "workflow_actor_id",
                "request_sha256", "title_sha256", "issue_binding_sha256", "release_tag",
                "approved_at_utc", "approval_id",
            },
        )
        self.assertEqual(value["request_sha256"], "a" * 64)
        self.assertEqual(value["title_sha256"], "b" * 64)
        self.assertEqual(value["issue_binding_sha256"], "e" * 64)
        self.assertEqual(value["workflow_run_id"], 123456789)
        self.assertEqual(value["workflow_run_attempt"], 1)
        self.assertEqual(value["workflow_actor_id"], ALLOWED_ACTOR_ID)
        self.assertNotIn("issue_body", value)
        self.assertNotIn("arguments", value)
        self.assertNotIn("private_key", value)

    def issue_event(self, *, action="opened", issue_user_id=ALLOWED_ACTOR_ID,
                    sender_id=ALLOWED_ACTOR_ID, repository_id=int(REPOSITORY_ID),
                    repository_name=REPOSITORY, title=None, body=None):
        release_tag = VALID_ENV["RELEASE_TAG"]
        payload = {
            "request_sha256": "a" * 64,
            "title_sha256": "b" * 64,
            "issue_binding_sha256": "e" * 64,
            "release_tag": release_tag,
            "confirmation": "I_APPROVE",
        }
        event = {
            "action": action,
            "issue": {
                "id": 1234,
                "number": 42,
                "state": "open",
                "title": title or "Sentinel command relay " + release_tag,
                "body": body if body is not None else json.dumps(payload, separators=(",", ":")),
                "user": {"id": issue_user_id},
            },
            "sender": {"id": sender_id},
            "repository": {"id": repository_id, "full_name": repository_name},
        }
        return event

    def test_builds_same_hash_only_schema_from_trusted_public_issue_event(self):
        event = self.issue_event()
        with tempfile.TemporaryDirectory() as directory:
            event_path = Path(directory) / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            env = dict(VALID_ENV)
            env.update({
                "GITHUB_EVENT_NAME": "issues",
                "GITHUB_EVENT_PATH": str(event_path),
                "REQUEST_SHA256": "",
                "TITLE_SHA256": "",
                "ISSUE_BINDING_SHA256": "",
                "RELEASE_TAG": "",
                "CONFIRMATION": "",
            })
            value = build_attestation(env)
        self.assertEqual(value["request_sha256"], "a" * 64)
        self.assertEqual(value["title_sha256"], "b" * 64)
        self.assertEqual(value["issue_binding_sha256"], "e" * 64)
        self.assertEqual(value["release_tag"], VALID_ENV["RELEASE_TAG"])
        self.assertNotIn("issue_id", value)
        self.assertNotIn("issue_number", value)
        self.assertNotIn("arguments", value)

    def test_issue_event_rejects_edited_action_wrong_author_or_repository(self):
        cases = (
            self.issue_event(action="edited"),
            self.issue_event(issue_user_id=ALLOWED_ACTOR_ID + 1),
            self.issue_event(sender_id=ALLOWED_ACTOR_ID + 1),
            self.issue_event(repository_id=int(REPOSITORY_ID) + 1),
            self.issue_event(repository_name="attacker/repo"),
        )
        for event in cases:
            with self.subTest(event=event):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "event.json"
                    path.write_text(json.dumps(event), encoding="utf-8")
                    env = dict(VALID_ENV, GITHUB_EVENT_NAME="issues", GITHUB_EVENT_PATH=str(path))
                    with self.assertRaises(ApprovalInputError):
                        build_attestation(env)

    def test_issue_event_rejects_unexpected_title_schema_and_confirmation(self):
        release_tag = VALID_ENV["RELEASE_TAG"]
        payload = {
            "request_sha256": "a" * 64,
            "title_sha256": "b" * 64,
            "issue_binding_sha256": "e" * 64,
            "release_tag": release_tag,
            "confirmation": "I_APPROVE",
        }
        bad_events = (
            self.issue_event(title="not the relay issue"),
            self.issue_event(body=json.dumps(dict(payload, private_issue_number=99))),
            self.issue_event(body=json.dumps(dict(payload, confirmation="CANCEL"))),
        )
        for event in bad_events:
            with self.subTest(event=event):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "event.json"
                    path.write_text(json.dumps(event), encoding="utf-8")
                    env = dict(VALID_ENV, GITHUB_EVENT_NAME="issues", GITHUB_EVENT_PATH=str(path))
                    with self.assertRaises(ApprovalInputError):
                        build_attestation(env)

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
            ("ISSUE_BINDING_SHA256", "not-a-binding-hash"),
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
