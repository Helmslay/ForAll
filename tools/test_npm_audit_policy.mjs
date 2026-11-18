import test from "node:test";
import assert from "node:assert/strict";
import { evaluateAuditReport, TEMPORARY_ALLOWED_ADVISORY } from "./npm_audit_policy.mjs";

const allowed = {
  picomatch: ["4.0.7", [TEMPORARY_ALLOWED_ADVISORY]],
  "@vue/language-core": ["3.3.14", ["picomatch"]],
  fdir: ["6.5.0", ["picomatch"]],
  tinyglobby: ["0.2.17", ["fdir", "picomatch"]],
  vite: ["8.3.8", ["picomatch", "tinyglobby"]],
  vitest: ["4.1.11", ["@vitest/mocker", "picomatch", "tinyglobby"]],
  "vue-tsc": ["3.3.14", ["@vue/language-core"]],
};

function fixtures(name = "picomatch", { dev = true, version, via } = {}) {
  const [expectedVersion, expectedVia] = allowed[name];
  const node = `node_modules/${name}`;
  return {
    report: {
      vulnerabilities: {
        [name]: {
          severity: "high",
          dev,
          nodes: [node],
          via: (via ?? expectedVia).map((item) =>
            item.startsWith("https://")
              ? { url: item }
              : item,
          ),
        },
      },
    },
    lockfile: {
      packages: {
        [node]: { version: version ?? expectedVersion, dev },
      },
    },
  };
}

test("accepts only the exact approved picomatch advisory and propagated dev-only paths", () => {
  for (const name of Object.keys(allowed)) {
    const { report, lockfile } = fixtures(name);
    const result = evaluateAuditReport(report, lockfile);
    assert.equal(result.accepted.length, 1, name);
    assert.equal(result.blocked.length, 0, name);
  }
});

test("blocks a production dependency", () => {
  const { report, lockfile } = fixtures("picomatch", { dev: false });
  assert.equal(evaluateAuditReport(report, lockfile).blocked.length, 1);
});

test("blocks an unexpected version", () => {
  const { report, lockfile } = fixtures("picomatch", { version: "4.0.8" });
  assert.equal(evaluateAuditReport(report, lockfile).blocked.length, 1);
});

test("blocks an unexpected dependency edge", () => {
  const { report, lockfile } = fixtures("vite", { via: ["picomatch", "unexpected-package"] });
  assert.equal(evaluateAuditReport(report, lockfile).blocked.length, 1);
});

test("blocks any other high-severity package", () => {
  const { report, lockfile } = fixtures();
  report.vulnerabilities.other = { severity: "high", dev: true, nodes: ["node_modules/other"], via: ["picomatch"] };
  lockfile.packages["node_modules/other"] = { version: "1.0.0", dev: true };
  assert.equal(evaluateAuditReport(report, lockfile).blocked.length, 1);
});
