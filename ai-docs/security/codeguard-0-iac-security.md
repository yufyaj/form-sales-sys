---
description: Infrastructure as Code Security
languages:
- c
- d
- javascript
- powershell
- ruby
- shell
- yaml
alwaysApply: false
---

rule_id: codeguard-0-iac-security

# Infrastructure as Code (IaC) Security

When designing cloud infrastructure and writing Infrastructure as Code (IaC) in languages like Terraform and CloudFormation, always use secure practices and defaults such as preventing public exposure and follow the principle of least privilege. Actively identify security misconfigurations and provide secure alternatives.

## Critical Security Patterns In Infrastructure as Code

### Network security
- **ALWAYS** restrict the access to remote administrative services, databases, LDAP, TACACS+, or other sensitive services. No service should be accessible from the entire Internet if it does not need to be. Instead, restrict access to a specific set of IP addresses or CIDR blocks which require access.
    - Security Group and ACL inbound rules should **NEVER** allow `0.0.0.0/0` to remote administration ports (such as SSH 22, RDP 3389).
    - Security Group and ACL inbound rules should **NEVER** allow `0.0.0.0/0` to database ports (such as 3306, 5432, 1433, 1521, 27017).
    - Kubernetes API endpoints allow lists should **NEVER** allow `0.0.0.0/0`. EKS, AKS, GKE, and any other Kubernetes API endpoint should be restricted to an allowed list of CIDR addresses which require administrative access.
    - **NEVER** expose cloud platform database services (RDS, Azure SQL, Cloud SQL) to all IP addresses `0.0.0.0/0`.
- Generally prefer private networking, such as internal VPC, VNET, VPN, or other internal transit unless public network access is required.
- **ALWAYS** enable VPC/VNET flow logs for network monitoring and security analysis.
- **ALWAYS** implement default deny rules and explicit allow rules for required traffic only.
- Generally prefer blocking egress traffic to the Internet by default. If egress is required appropriate traffic control solutions might include:
    - Egress firewall or proxy with rules allowing access to specific required services.
    - Egress security group (SG) or access control list (ACL) with rules allowing access to specific required IPs or CIDR blocks.
    - DNS filtering to prevent access to malicious domains.

### Data protection
- **ALWAYS** configure data encryption at rest for all storage services including databases, file systems, object storage, and block storage.
    - Enable encryption for cloud storage services (S3, Azure Blob, GCS buckets).
    - Configure database encryption at rest for all database engines (RDS, Azure SQL, Cloud SQL, DocumentDB, etc.).
    - Enable EBS/disk encryption for virtual machine storage volumes.
- **ALWAYS** configure encryption in transit for all data communications.
    - Use TLS 1.2 or higher for all HTTPS/API communications.
    - Configure SSL/TLS for database connections with certificate validation.
    - Enable encryption for inter-service communication within VPCs/VNETs.
    - Use encrypted protocols for remote access (SSH, HTTPS, secure RDP).
- **ALWAYS** implement data classification and protection controls based on sensitivity levels.
    - Apply stricter encryption and access controls for PII, PHI, financial data, and intellectual property.
    - Use separate encryption keys for different data classification levels.
- **ALWAYS** configure secure data retention and disposal policies.
    - Define data retention periods based on regulatory and business requirements.
    - Implement automated data lifecycle management with secure deletion.
- **ALWAYS** enable comprehensive data access monitoring and auditing.
    - Log all data access, modification, and deletion operations.
    - Monitor for unusual data access patterns and potential data exfiltration.
    - Implement real-time alerting for sensitive data access violations.
- **ALWAYS** encrypt data backups.
    - Encrypt all backup data using separate encryption keys from production data.
    - Store backups in geographically distributed locations with appropriate access controls.
    - Test backup restoration procedures regularly and verify backup integrity.

### Access control
- **NEVER** leave critical administration or data services with anonymous access (backups, storage, container registries, file shares) unless otherwise labeled as public classification or intended to be public.
- **NEVER** use wildcard permissions in IAM policies or cloud RBAC (`"Action": "*"`, `"Resource": "*"`)
- **NEVER** overprivilege service accounts with Owner/Admin roles when it is not necessary.
- **NEVER** use service API Keys and client secrets and instead use workload identity with role-based access control to eliminate the need for long-lived credentials.
- **NEVER** enable or use the legacy Instance Metadata Service version 1 (IMDSv1) in AWS.
- **NEVER** use legacy or outdated authentication methods (such as local users) when there is a more secure alternative such as OAuth.

### Container and VM images
- **NEVER** use non-hardened VM and container images.
- **ALWAYS** choose distroless or minimal container images.
- **RECOMMEND** using secure baseline virtual machine images from trusted sources.
- **RECOMMEND** using minimal distroless container images from trusted sources.

### Logging and administrative access
- **NEVER** disable administrative activity logging for sensitive services.
- **ALWAYS** enable audit logging for privileged operations.

### Secrets management
- **NEVER** hardcode secrets, passwords, API keys, or certificates directly in IaC source code.
- **ALWAYS** in Terraform mark secrets with "sensitive = true", in other IaC code use appropriate annotations or metadata to indicate sensitive values.

### Backup and data recovery
- **NEVER** create backups without encryption at rest and in transit.
- **ALWAYS** configure multi-region data storage for backups with cross-region replication.
- **NEVER** configure backups without retention policies and lifecycle management.
