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
   pinned workflow/helper file blob SHAs, actor ID, run success and timestamp interval;
5. reject expired, mismatched, copied or missing attestations;
6. require that the current Issue remains eligible for signing and let the existing durable issuer outbox, monotonic sequence and Issue state transition prevent a second publication. A release tag cannot be re-created in GitHub; the Issue binding prevents copying the attestation to a different Issue;
7. only then create the local Ed25519 envelope and publish the typed request.

The private VPS remains the trust decision point. No private signing key is
present in ForAll or in GitHub Actions.

## Workflow

Workflow: `.github/workflows/sentinel-control-command-approval.yml`

1. Prepare an open, unapproved typed Issue in the private
   `Helmslay/sentinel-explorer-agent` repository.
2. A human changes only its title to begin with `[APPROVED] `. That title
   transition remains the explicit authorization signal.
3. A trusted integration creates a public relay Issue in `Helmslay/ForAll`
   containing only the request hash, approved-title hash, opaque private-Issue
   binding hash, fresh release tag and `I_APPROVE`. It does not copy the
   private Issue number, title, body, operation or arguments.
4. The `issues.opened` workflow runs on GitHub-hosted infrastructure, checks
   the event actor and Issue author against the configured operator identity,
   validates the exact payload schema, then publishes one prerelease with
   exactly one asset: `approval-attestation.json`.
5. The private VPS independently validates the workflow run, pinned files,
   timestamp, hashes and private Issue identity before its local Ed25519 signer
   may issue the command envelope.

The previous `workflow_dispatch` path remains available as a manual recovery
path. A successful public run only means that an attestation was emitted; it
does not mean that the private VPS accepted, signed or executed the request.

## Offline validation

From the repository root:

```bash
python -m unittest discover -s tools -p 'test_*.py' -v
python -m py_compile tools/sentinel_control_relay/approval.py tools/sentinel_control_relay/test_approval.py
```

The tests use only the Python standard library and do not contact GitHub or the
private repository.

## Integration status

The public attestation generator and workflow are implemented here. The private Sentinel verifier is merged and pins the workflow/helper blob SHA values above at the public run's source SHA. Documentation-only commits on ForAll main do not invalidate the pin; changes to either executable file require a reviewed private trust-anchor update. The private changes are not deployed on the VPS yet; a generated public attestation must not be treated as an executable approval until guarded deployment and a live read-only result test complete.
