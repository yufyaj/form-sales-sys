---
description: Kubernetes hardening (RBAC, admission policies, network policies, secrets, supply chain)
languages:
- javascript
- yaml
alwaysApply: false
---

rule_id: codeguard-0-cloud-orchestration-kubernetes

## Cloud & Orchestration (Kubernetes)

Kubernetes cluster and workload hardening: identity, policy, networking, secrets, and supply chain controls.

### Controls
- Identity & RBAC: least privilege for users and service accounts; separate namespaces; bind only needed roles.
- Policy: admission controls (OPA/Gatekeeper/Kyverno) for image sources, capabilities, root, network policies, and required labels/annotations.
- Networking: default‑deny with network policies; explicit egress allow‑lists; service identity/mTLS within mesh where applicable.
- Secrets: use KMS providers; avoid plaintext in manifests; rotate regularly; restrict secret mount paths.
- Nodes: hardened OS, auto‑updates, minimal attack surface; isolate sensitive workloads with taints/tolerations and dedicated nodes.
- Supply chain: verify image signatures; enforce provenance (SLSA/Sigstore) in admission.

### Checklist
- Namespaces per team/app; RBAC roles scoped; audit logging enabled.
- Admission policies enforce image provenance, non‑root, dropped capabilities, read‑only root FS, and network policy presence.
- Network policies in place for ingress/egress; service accounts scoped per deployment.

### Verification
- Cluster conformance and CIS benchmark scans.
- Policy tests in CI for manifests (OPA unit tests); periodic admission dry‑run.

### Incident Readiness
- Enable audit logs and centralize; restrict access to etcd; backup/restore tested.
- Define break‑glass roles with MFA and time‑bound approvals.
