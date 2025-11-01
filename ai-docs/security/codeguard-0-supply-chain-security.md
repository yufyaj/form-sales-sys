---
description: Dependency & supply chain security (pinning, SBOM, provenance, integrity, private registries)
languages:
- docker
- javascript
- yaml
alwaysApply: false
---

rule_id: codeguard-0-supply-chain-security

## Dependency & Supply Chain Security

Control third‑party risk across ecosystems, from selection and pinning to provenance, scanning, and rapid response.

### Policy and Governance
- Maintain allow‑listed registries and scopes; disallow direct installs from untrusted sources.
- Require lockfiles and version pinning; prefer digest pinning for images and vendored assets.
- Generate SBOMs for apps/images; store with artifacts; attest provenance (SLSA, Sigstore).

### Package Hygiene (npm focus applicable to others)
- Regularly audit (`npm audit`, ecosystem SCA) and patch; enforce SLAs by severity.
- Use deterministic builds: `npm ci` (not `npm install`) in CI/CD; maintain lockfile consistency.
- Avoid install scripts that execute on install when possible; review for risk.
- Use `.npmrc` to scope private registries; avoid wildcard registries; enable integrity verification.
- Enable account 2FA for publishing

### Development Practices
- Minimize dependency footprint; remove unused packages; prefer stdlib/first‑party for trivial tasks.
- Protect against typosquatting and protestware: pin maintainers, monitor releases, and use provenance checks.
- Hermetic builds: no network in compile/packaging stages unless required; cache with authenticity checks.

### CI/CD Integration
- SCA, SAST, IaC scans in gates; fail on criticals; require approvals for overrides with compensating controls.
- Sign artifacts; verify signatures at deploy; enforce policy in admission.

### Vulnerability Management
- For patched vulnerabilities: test and deploy updates; document any API breaking changes.
- For unpatched vulnerabilities: implement compensating controls (input validation, wrappers) based on CVE type; prefer direct dependency fixes over transitive workarounds.
- Document risk decisions; escalate acceptance to appropriate authority with business justification.

### Incident Response
- Maintain rapid rollback; isolate compromised packages; throttle rollouts; notify stakeholders.
- Monitor threat intel feeds (e.g., npm advisories); auto‑open tickets for critical CVEs.

### Implementation Checklist
- Lockfiles present; integrity checks on; private registries configured.
- SBOM + provenance stored; signatures verified pre‑deploy.
- Automated dependency updates with tests and review gates.
- High‑sev vulns remediated within SLA or mitigated and documented.
