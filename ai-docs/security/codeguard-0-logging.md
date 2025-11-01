---
description: Logging & monitoring (structured telemetry, redaction, integrity, detection & alerting)
languages:
- c
- javascript
- yaml
alwaysApply: false
---

rule_id: codeguard-0-logging

## Logging & Monitoring

Produce structured, privacy‑aware telemetry that supports detection, response, and forensics without exposing secrets.

### What to Log
- Authn/authz events; admin actions; config changes; sensitive data access; input validation failures; security errors.
- Include correlation/request IDs, user/session IDs (non‑PII), source IP, user agent, timestamps (UTC, RFC3339).

### How to Log
- Structured logs (JSON) with stable field names; avoid free‑form text for critical signals.
- Sanitize all log inputs to prevent log injection (strip CR/LF/delimiters); validate data from other trust zones.
- Redact/tokenize secrets and sensitive fields; never log credentials, tokens, recovery codes, or raw session IDs.
- Ensure integrity: append‑only or WORM storage; tamper detection; centralized aggregation; access controls and retention policies.

### Detection & Alerting
- Build alerts for auth anomalies (credential stuffing patterns, impossible travel), privilege changes, excessive failures, SSRF indicators, and data exfil patterns.
- Tune thresholds; provide runbooks; ensure on‑call coverage; test alert flows.

### Storage & Protection
- Isolate log storage (separate partition/database); strict file/directory permissions; store outside web‑accessible locations.
- Synchronize time across systems; use secure protocols for transmission; implement tamper detection and monitoring.

### Privacy & Compliance
- Maintain data inventory and classification; minimize personal data in logs; honor retention and deletion policies.
- Provide mechanisms to trace and delete user‑linked log data where required by policy.

### Implementation Checklist
- JSON logging enabled; log injection sanitization active; redaction filters active; correlation IDs on all requests.
- Isolated log storage with tamper detection; centralized log pipeline with integrity protections; retention configured.
- Security alerts defined and tested; dashboards and reports in place.

### Validation
- Unit/integration tests assert presence/absence of key fields; redaction unit tests.
- Periodic audits for secret/PII leakage; tabletop exercises for incident workflows.
