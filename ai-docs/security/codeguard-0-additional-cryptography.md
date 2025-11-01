---
description: Additional Cryptography guidance
languages:
- c
- go
- java
- javascript
- kotlin
- matlab
- php
- python
- ruby
- swift
- typescript
- xml
- yaml
alwaysApply: false
---

rule_id: codeguard-0-additional-cryptography

## Additional Cryptography & TLS

Apply modern, vetted cryptography for data at rest and in transit. Manage keys safely, configure TLS correctly, deploy HSTS, and consider pinning only when appropriate.

### Algorithms and Modes
- Symmetric: AES‑GCM or ChaCha20‑Poly1305 preferred. Avoid ECB. CBC/CTR only with encrypt‑then‑MAC.
- Asymmetric: RSA ≥2048 or modern ECC (Curve25519/Ed25519). Use OAEP for RSA encryption.
- Hashing: SHA‑256+ for integrity; avoid MD5/SHA‑1.
- RNG: Use CSPRNG appropriate to platform (e.g., SecureRandom, crypto.randomBytes, secrets module). Never use non‑crypto RNGs.

### Key Management
- Generate keys within validated modules (HSM/KMS) and never from passwords or predictable inputs.
- Separate keys by purpose (encryption, signing, wrapping). Rotate on compromise, cryptoperiod, or policy.
- Store keys in KMS/HSM or vault; never hardcode; avoid plain env vars. Use KEK to wrap DEKs; store separately.
- Control access to trust stores; validate updates; audit all key access and operations.

### Data at Rest
- Encrypt sensitive data; minimize stored secrets; tokenize where possible.
- Use authenticated encryption; manage nonces/IVs properly; keep salts unique per item.
- Protect backups: encrypt, restrict access, test restores, manage retention.

### TLS Configuration
- Protocols: TLS 1.3 preferred; allow TLS 1.2 only for legacy compatibility; disable TLS 1.0/1.1 and SSL. Enable TLS_FALLBACK_SCSV.
- Ciphers: prefer AEAD suites; disable NULL/EXPORT/anon. Keep libraries updated; disable compression.
- Key exchange groups: prefer x25519/secp256r1; configure secure FFDHE groups if needed.
- Certificates: 2048‑bit+ keys, SHA‑256, correct CN/SAN. Manage lifecycle and revocation (OCSP stapling).
- Application: HTTPS site‑wide; redirect HTTP→HTTPS; prevent mixed content; set cookies `Secure`.

### HSTS
- Send Strict‑Transport‑Security only over HTTPS. Phase rollout:
  - Test: short max‑age (e.g., 86400) with includeSubDomains
  - Prod: ≥1 year max‑age; includeSubDomains when safe
  - Optional preload once mature; understand permanence and subdomain impact

### Pinning
- Avoid browser HPKP. Consider pinning only for controlled clients (e.g., mobile) and when you own both ends.
- Prefer SPKI pinning with backup pins; plan secure update channels; never allow user bypass.
- Thoroughly test rotation and failure handling; understand operational risk.

### Implementation Checklist
- AEAD everywhere; vetted libraries only; no custom crypto.
- Keys generated and stored in KMS/HSM; purpose‑scoped; rotation documented.
- TLS 1.3/1.2 with strong ciphers; compression off; OCSP stapling on.
- HSTS deployed per phased plan; mixed content eliminated.
- Pinning used only where justified, with backups and update path.

### Test Plan
- Automated config scans (e.g., SSL Labs, testssl.sh) for protocol/cipher/HSTS.
- Code review for crypto API misuse; tests for key rotation, backup/restore.
- Pinning simulations for rotation/failures if deployed.
