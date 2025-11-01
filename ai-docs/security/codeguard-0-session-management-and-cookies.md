---
description: Session management and secure cookies (rotation, fixation, timeouts, theft detection)
languages:
- c
- go
- html
- java
- javascript
- php
- python
- ruby
- typescript
alwaysApply: false
---

rule_id: codeguard-0-session-management-and-cookies

## Session Management & Cookies

Implement robust, attack-resistant session handling that prevents fixation, hijacking, and theft while maintaining usability.

### Session ID Generation and Properties
- Generate session IDs with a CSPRNG; ≥64 bits of entropy (prefer 128+). Opaque, unguessable, and free of meaning.
- Use generic cookie names (e.g., `id`) rather than framework defaults. Reject any incoming ID not created by the server.
- Store all session data server-side; never embed PII or privileges in the token. If sensitive, encrypt server-side session store at rest.

### Cookie Security Configuration
- Set `Secure`, `HttpOnly`, `SameSite=Strict` (or `Lax` if necessary for flows) on session cookies.
- Scope cookies narrowly with `Path` and `Domain`. Avoid cross-subdomain exposure.
- Prefer non-persistent session cookies (no Expires/Max-Age). Require full HTTPS; enable HSTS site-wide.

Example header:
```
Set-Cookie: id=<opaque>; Secure; HttpOnly; SameSite=Strict; Path=/
```

### Session Lifecycle and Rotation
- Create sessions only server-side; treat provided IDs as untrusted input.
- Regenerate session ID on authentication, password changes, and any privilege elevation. Invalidate the prior ID.
- Use distinct pre‑auth and post‑auth cookie names if framework patterns require it.

### Expiration and Logout
- Idle timeout: 2–5 minutes for high-value, 15–30 minutes for lower risk. Absolute timeout: 4–8 hours.
- Enforce timeouts server-side. Provide a visible logout button that fully invalidates the server session and clears the cookie client-side.

### Transport and Caching
- Enforce HTTPS for the entire session journey. Never mix HTTP/HTTPS in one session.
- Send `Cache-Control: no-store` on responses containing session identifiers or sensitive data.

### Cookie Theft Detection and Response
- Fingerprint session context server-side at establishment (IP, User-Agent, Accept-Language, relevant `sec-ch-ua` where available).
- Compare incoming requests to the stored fingerprint, allowing for benign drift (e.g., subnet changes, UA updates).
- Risk-based responses:
  - High risk: require re-authentication; rotate session ID.
  - Medium risk: step-up verification (challenge); rotate session ID.
  - Low risk: log suspicious activity.
- Always regenerate the session ID when potential hijacking is detected.

### Client-Side Storage
- Do not store session tokens in `localStorage`/`sessionStorage` due to XSS risk. Prefer HttpOnly cookies for transport.
- If client-side storage is unavoidable for non-session secrets, isolate via Web Workers and never expose in page context.

### Framework and Multi-Cookie Scenarios
- Prefer built-in session frameworks; keep them updated and hardened.
- Validate relationships when multiple cookies participate in session state; avoid same cookie names across paths/domains.

### Monitoring and Telemetry
- Log session lifecycle events (creation, rotation, termination) using salted hashes of the session ID, not raw values.
- Monitor for brute force of session IDs and anomalous concurrent usage.

### Implementation Checklist
1) CSPRNG session IDs (≥64 bits entropy), opaque and server-issued only.
2) Cookie flags: `Secure`, `HttpOnly`, `SameSite` set; tight domain/path.
3) HTTPS-only with HSTS; no mixed content.
4) Regenerate IDs on auth and privilege changes; invalidate old IDs.
5) Idle and absolute timeouts enforced server-side; full logout implemented.
6) `Cache-Control: no-store` for sensitive responses.
7) Server-side fingerprinting and risk-based responses to anomalies.
8) No client storage of session tokens; framework defaults hardened.
