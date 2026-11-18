export const TEMPORARY_ALLOWED_ADVISORY = "https://github.com/advisories/GHSA-fc5q-39xc-vjpf";
export const TEMPORARY_ALLOWED_PACKAGE = "picomatch";
export const TEMPORARY_ALLOWED_VERSION = "4.0.7";

export function evaluateAuditReport(report, lockfile) {
  if (!report || typeof report !== "object" || !report.vulnerabilities) {
    throw new TypeError("npm audit report has no vulnerabilities object");
  }

  const blocked = [];
  const accepted = [];

  for (const [name, vulnerability] of Object.entries(report.vulnerabilities)) {
    if (!["high", "critical"].includes(vulnerability.severity)) continue;

    const nodes = Array.isArray(vulnerability.nodes) ? vulnerability.nodes : [];
    const via = Array.isArray(vulnerability.via) ? vulnerability.via : [];
    const packagePath = nodes.length === 1 ? nodes[0] : null;
    const installed = packagePath ? lockfile?.packages?.[packagePath] : null;
    const exactException =
      name === TEMPORARY_ALLOWED_PACKAGE &&
      vulnerability.dev === true &&
      packagePath === "node_modules/picomatch" &&
      installed?.version === TEMPORARY_ALLOWED_VERSION &&
      installed?.dev === true &&
      via.length > 0 &&
      via.every(
        (item) =>
          item &&
          typeof item === "object" &&
          item.url === TEMPORARY_ALLOWED_ADVISORY,
      );

    if (exactException) {
      accepted.push({ name, severity: vulnerability.severity, packagePath });
    } else {
      blocked.push({ name, severity: vulnerability.severity, nodes, via });
    }
  }

  return { accepted, blocked };
}
