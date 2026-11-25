# OPS-CTRL-01 — public hash-only Sentinel command approval relay

**Status:** IN_REVIEW — public code merged; live workflow smoke and private verifier remain  
**Owner authorization:** explicit user direction, 2026-11-25  
**Dependencies:** existing ForAll public release relay; Sentinel VPS-local Ed25519 signer design  
**Goal:** add an isolated, public GitHub Actions relay in ForAll that attests to approval of a private Sentinel command using only SHA-256 hashes, without using the private repository's hosted Actions quota or the blocked Windows/Kaspersky runner registration path.

## Scope

- Add `tools/sentinel_control_relay/` with an isolated standard-library attestation builder, tests and operator README.
- Add a dedicated `workflow_dispatch` workflow on ForAll `main`.
- Limit it to the configured operator numeric ID and login.
- Publish exactly one public asset, `approval-attestation.json`, with request/title hashes and public workflow identity.
- Add the module to the existing offline tools test workflow.
- Record architecture and operating constraints in `docs/DECISIONS.md`.

## Explicit non-goals

- Do not modify the existing site publication relay or its trust anchor.
- Do not send private Issue data, command arguments, keys or tokens to ForAll.
- Do not sign commands or execute them in the public workflow.
- Do not change Sentinel VPS services, keyrings, sequence state or replay ledgers.
- Do not change Pocket Forester or either Windows runner installation.
- Do not claim end-to-end Sentinel command approval until the private verifier is integrated and independently tests the public workflow run.

## Acceptance criteria

1. The workflow can only complete on ForAll `main`, from the configured owner identity, on the exact workflow path and first run attempt.
2. Invalid repository/ref/event/actor/hash/tag/confirmation inputs are rejected by the pure attestation builder.
3. The output schema has no raw Issue content, arguments, credentials or signing key.
4. The public Release carries only one asset named `approval-attestation.json`.
5. Offline unit tests and Python compilation pass on Python 3.12.
6. Existing site-publication relay workflow remains unchanged.
7. Project decision and operating limitations are documented.

## Result — 2026-11-25

- PR #72 merged: `2b8127669f3b368e8b801b1d6cb225f65c12272b`.
- Exact PR head: `271a3d7630ed15d1287eeb8ecd62665eaac8f679`.
- Tools offline tests run `45607534453` — SUCCESS; all 27 tests passed, including 4 relay tests.
- Frontend build/Compose run `45607534618` — SUCCESS.
- GitLab mirror run `45607524536` — SUCCESS.
- The manual `workflow_dispatch` has not been executed. Private Sentinel verifier integration is not merged or deployed.

## Validation

- `python -m unittest discover -s tools -p 'test_*.py' -v`
- `python -m py_compile tools/sentinel_control_relay/approval.py tools/sentinel_control_relay/test_approval.py`
- Exact-head GitHub Actions **Tools offline tests** on the PR.

## Follow-up dependency

A separate Sentinel Agent task must implement the private-side lookup and exact-run verification, bind the release tag into the private request metadata without passing it to the signed operation arguments, retire the issue-triggered private Windows approval workflow, run CircleCI Python 3.11/3.14, and test the complete read-only flow. The VPS must not consume this public attestation before that work is merged and deployed.
