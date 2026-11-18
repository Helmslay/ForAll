export const TEMPORARY_ALLOWED_ADVISORY = "https://github.com/advisories/GHSA-fc5q-39xc-vjpf";

// Exact dev-only dependency graph observed in the reviewed lockfile and npm audit report.
// Keep this list narrow; any changed package, version, path or dependency edge fails closed.
const ALLOWED_HIGH_PATHS = {
  "picomatch": { version: "4.0.7", via: [TEMPORARY_ALLOWED_ADVISORY] },
  "@vue/language-core": { version: "3.3.14", via: ["picomatch"] },
  "fdir": { version: "6.5.0", via: ["picomatch"] },
  "tinyglobby": { version: "0.2.17", via: ["fdir", "picomatch"] },
  "vite": { version: "8.3.8", via: ["picomatch", "tinyglobby"] },
  "vitest": { version: "4.1.11", via: ["@vitest/mocker", "picomatch", "tinyglobby"] },
  "vue-tsc": { version: "3.3.14", via: ["@vue/language-core"] },
};

export function evaluateAuditReport(report, lockfile) {
  if (!report || typeof report !== "object" || !report.vulnerabilities) {
    throw new TypeError("npm audit report has no vulnerabilities object");
  }

  const blocked = [];
  const accepted = [];

  for (const [name, vulnerability] of Object.entries(report.vulnerabilities)) {
    if (!["high", "critical"].includes(vulnerability.severity)) continue;

    const expected = ALLOWED_HIGH_PATHS[name];
    const nodes = Array.isArray(vulnerability.nodes) ? vulnerability.nodes : [];
    const via = Array.isArray(vulnerability.via) ? vulnerability.via : [];
    const packagePath = nodes.length === 1 ? nodes[0] : null;
    const installed = packagePath ? lockfile?.packages?.[packagePath] : null;
    const actualVia = via.map((item) =>
      typeof item === "string" ? item : item?.url ?? null,
    );

    const exactException =
      Boolean(expected) &&
      packagePath === `node_modules/${name}` &&
      installed?.version === expected.version &&
      installed?.dev === true &&
      actualVia.length === expected.via.length &&
      actualVia.every((item, index) => item === expected.via[index]);

    if (exactException) {
      accepted.push({ name, severity: vulnerability.severity, packagePath });
    } else {
      blocked.push({ name, severity: vulnerability.severity, nodes, via, lockfileVersion: installed?.version, lockfileDev: installed?.dev, auditDev: vulnerability.dev });
    }
  }

  return { accepted, blocked };
}
