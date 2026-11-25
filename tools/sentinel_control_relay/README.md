# Sentinel command approval relay

This folder contains the public, hash-only approval relay used by the private
`Helmslay/sentinel-explorer-agent` control plane. It is deliberately separate
from the Sentinel Explorer Web application and from the existing site-release
relay.

## Security boundary

The public workflow receives only:

- SHA-256 of the exact raw JSON body of one private Sentinel Issue;
- SHA-256 of its exact approved title (including the `[APPROVED] ` prefix);
- SHA-256 of a canonical binding that includes the private repository ID, Issue ID/number, request hash, title hash, unique release tag and a per-request random nonce. The workflow never receives the nonce or the Issue identifiers.
- a fresh, opaque release tag `sentinel-command-<32 lowercase hex>`;
- an explicit `I_APPROVE` confirmation.

It must never receive the private Issue URL/number, raw title/body, operation,
arguments, GitHub App credentials, VPS credentials, or Ed25519 key material.
The workflow is pinned to this public repository's `main` branch and to the
single operator identity configured in the code and workflow.

The relay creates one public prerelease containing only
`approval-attestation.json`. The attestation contains the hashes, one-time
release tag, operator identity, workflow path/SHA/run identity, timestamp and
random approval UUID. It is **not** a command signature and does not authorize
execution by itself.

The private VPS must independently:

1. fetch the current private Issue using its own narrowly scoped GitHub App;
2. validate requester, state, title transition, request schema and operation
   allowlist;
3. compare both raw SHA-256 values with the attestation;
4. verify the exact public workflow run, attempt, repository ID, workflow path,
   pinned `main` commit, actor ID, run success and timestamp interval;
5. reject expired, mismatched, reused or missing attestations;
6. recompute and compare the opaque Issue binding, then reserve the attestation ID/tag in a durable private approval replay ledger;
7. only then create the local Ed25519 envelope and publish the typed request.

The private VPS remains the trust decision point. No private signing key is
present in ForAll or in GitHub Actions.

## Workflow

Workflow: `.github/workflows/sentinel-control-command-approval.yml`

1. Prepare an open, unapproved Issue in `Helmslay/sentinel-explorer-agent`.
2. Make the final intended title begin with `[APPROVED] `.
3. Compute SHA-256 over the **exact raw UTF-8 Issue body** and exact title. Generate a fresh random approval nonce and compute the opaque binding hash over the private repository ID, Issue ID/number, both hashes, release tag and nonce using the private canonical JSON profile.
4. Generate a new `sentinel-command-<32 lowercase hex>` tag. The same tag must
   not be reused for another request.
5. In public `Helmslay/ForAll`, open Actions → **Sentinel Control Command
   Approval** → Run workflow on `main`; supply the two content hashes, the opaque Issue-binding hash, the tag and
   select `I_APPROVE` only after reviewing the pair.
6. The public workflow validates its own repository/ref/workflow/actor context,
   writes the hash-only attestation and creates a prerelease with exactly one
   asset: `approval-attestation.json`.

A successful public run only means that an attestation was emitted. It does not
mean that the private VPS accepted, signed or executed the request.

## Offline validation

From the repository root:

```bash
python -m unittest discover -s tools -p 'test_*.py' -v
python -m py_compile tools/sentinel_control_relay/approval.py tools/sentinel_control_relay/test_approval.py
```

The tests use only the Python standard library and do not contact GitHub or the
private repository.

## Integration status

The public attestation generator and workflow are implemented here. The private
Sentinel verifier must pin the exact merged ForAll workflow commit and add the
corresponding approval lookup before typed commands can use this route. Until
that private integration is reviewed and deployed, keep using the already
confirmed read-only Issue #56 history as historical evidence only; do not treat
a new public release as an executable approval.
