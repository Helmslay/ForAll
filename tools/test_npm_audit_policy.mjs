import test from "node:test";
import assert from "node:assert/strict";
import { evaluateAuditReport } from "./npm_audit_policy.mjs";

const advisory = "https://github.com/advisories/GHSA-fc5q-39xc-vjpf";
function report({ dev = true, version = "4.0.7", url = advisory, name = "picomatch" } = {}) {
  return {
    vulnerabilities: {
      [name]: {
        severity: "high",
        dev,
        nodes: ["node_modules/picomatch"],
        via: [{ url }],
      },
    },
  };
}
function lockfile({ version = "4.0.7", dev = true } = {}) {
  return { packages: { "node_modules/picomatch": { version, dev } } };
}

test("accepts only the explicitly approved devDependency advisory and exact version", () => {
  const result = evaluateAuditReport(report(), lockfile());
  assert.equal(result.accepted.length, 1);
  assert.equal(result.blocked.length, 0);
});

test("blocks the same advisory when it affects a production dependency", () => {
  assert.equal(evaluateAuditReport(report({ dev: false }), lockfile({ dev: false })).blocked.length, 1);
});

test("blocks a different version", () => {
  assert.equal(evaluateAuditReport(report({ version: "4.0.8" }), lockfile({ version: "4.0.8" })).blocked.length, 1);
});

test("blocks any other high advisory", () => {
  assert.equal(evaluateAuditReport(report({ url: "https://example.invalid/advisory" }), lockfile()).blocked.length, 1);
});

test("blocks any other high-severity package", () => {
  assert.equal(evaluateAuditReport(report({ name: "other-package" }), lockfile()).blocked.length, 1);
});
