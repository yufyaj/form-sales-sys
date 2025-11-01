---
description: API & Web services security (REST/GraphQL/SOAP), schema validation, authn/z, SSRF
languages:
- c
- go
- java
- javascript
- php
- python
- ruby
- typescript
- xml
- yaml
alwaysApply: false
---

rule_id: codeguard-0-api-web-services

## API & Web Services Security

Secure REST, GraphQL, and SOAP/WS services end‑to‑end: transport, authn/z, schema validation, SSRF controls, DoS limits, and microservice‑safe patterns.

### Transport and TLS
- HTTPS only; consider mTLS for high‑value/internal services. Validate certs (CN/SAN, revocation) and prevent mixed content.

### Authentication and Tokens
- Use standard flows (OAuth2/OIDC) for clients; avoid custom schemes. For services, use mTLS or signed service tokens.
- JWTs: pin algorithms; validate iss/aud/exp/nbf; short lifetimes; rotation; denylist on logout/revoke. Prefer opaque tokens when revocation is required and central store is available.
- API keys: scope narrowly; rate limit; monitor usage; do not use alone for sensitive operations.

### Authorization
- Enforce per‑endpoint, per‑resource checks server‑side; deny by default.
- For microservices, authorize at gateway (coarse) and service (fine) layers; propagate signed internal identity, not external tokens.

### Input and Content Handling
- Validate inputs via contracts: OpenAPI/JSON Schema, GraphQL SDL, XSD. Reject unknown fields and oversize payloads; set limits.
- Content types: enforce explicit Content‑Type/Accept; reject unsupported combinations. Harden XML parsers against XXE/expansion.

### SQL/Injection Safety in Resolvers and Handlers
- Use parameterized queries/ORM bind parameters; never concatenate user input into queries or commands.

### GraphQL‑Specific Controls
- Limit query depth and overall complexity; enforce pagination; timeouts on execution; disable introspection and IDEs in production.
- Implement field/object‑level authorization to prevent IDOR/BOLA; validate batching and rate limit per object type.

### SSRF Prevention for Outbound Calls
- Do not accept raw URLs. Validate domains/IPs using libraries; restrict to HTTP/HTTPS only (block file://, gopher://, ftp://, etc.).
- Case 1 (fixed partners): strict allow‑lists; disable redirects; network egress allow‑lists.
- Case 2 (arbitrary): block private/link‑local/localhost ranges; resolve and verify all IPs are public; require signed tokens from the target where feasible.

### SOAP/WS and XML Safety
- Validate SOAP payloads with XSD; limit message sizes; enable XML signatures/encryption where required.
- Configure parsers against XXE, entity expansion, and recursive payloads; scan attachments.

### Rate Limiting and DoS
- Apply per‑IP/user/client limits, circuit breakers, and timeouts. Use server‑side batching and caching to reduce load.

### Management Endpoints
- Do not expose over the Internet. Require strong auth (MFA), network restrictions, and separate ports/hosts.

### Testing and Assessment
- Maintain formal API definitions; drive contract tests and fuzzing from specs.
- Assess endpoints for authn/z bypass, SSRF, injection, and information leakage; log token validation failures.

### Microservices Practices
- Policy‑as‑code with embedded decision points; sidecar or library PDPs.
- Service identity via mTLS or signed tokens; never reuse external tokens internally.
- Centralized structured logging with correlation IDs; sanitize sensitive data.

### Implementation Checklist
- HTTPS/mTLS configured; certs managed; no mixed content.
- Contract validation at the edge and service; unknown fields rejected; size/time limits enforced.
- Strong authn/z per endpoint; GraphQL limits applied; introspection disabled in prod.
- SSRF protections at app and network layers; redirects disabled; allow‑lists where possible.
- Rate limiting, circuit breakers, and resilient patterns in place.
- Management endpoints isolated and strongly authenticated.
- Logs structured and privacy‑safe with correlation IDs.

### Test Plan
- Contract tests for schema adherence; fuzzing with schema‑aware tools.
- Pen tests for SSRF, IDOR/BOLA, and authz bypass; performance tests for DoS limits.
- Test all HTTP methods per endpoint; discover parameters in URL paths, headers, and structured data beyond obvious query strings.
- Automated checks for token validation and revocation behavior.
