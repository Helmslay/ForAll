import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { evaluateAuditReport } from "./npm_audit_policy.mjs";

const result = spawnSync("npm", ["audit", "--audit-level=high", "--json"], {
  encoding: "utf8",
  maxBuffer: 10 * 1024 * 1024,
});

if (result.error) {
  console.error("Unable to execute npm audit:", result.error.message);
  process.exit(2);
}

let report;
try {
  report = JSON.parse(result.stdout);
} catch {
  console.error("npm audit did not return valid JSON.");
  if (result.stderr) console.error(result.stderr);
  process.exit(2);
}

const lockfile = JSON.parse(readFileSync("package-lock.json", "utf8"));
const { accepted, blocked } = evaluateAuditReport(report, lockfile);
const counts = report.metadata?.vulnerabilities ?? {};
console.log("npm audit severity counts:", JSON.stringify(counts));

if (accepted.length) {
  console.warn(
    "TEMPORARY RISK ACCEPTANCE: allowing only the exact dev-only dependency paths propagated from " +
      "picomatch@4.0.7 / GHSA-fc5q-39xc-vjpf. This is not remediation; review and remove " +
      "the exception when an upstream fix is available.",
  );
}

if (blocked.length) {
  console.error("Unaccepted high/critical advisories:", JSON.stringify(blocked));
  process.exit(1);
}

if (result.status !== 0 && accepted.length === 0) {
  console.error("npm audit exited non-zero without an explicitly accepted advisory.");
  process.exit(1);
}

console.log("npm audit policy check passed.");
