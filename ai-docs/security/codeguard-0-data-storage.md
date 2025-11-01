---
description: Data & storage security (DB isolation, TLS, least privilege, RLS/CLS, backups, auditing)
languages:
- c
- javascript
- sql
- yaml
alwaysApply: false
---

rule_id: codeguard-0-data-storage

## Database Security Guidelines

This rule advises on securely configuring SQL and NoSQL databases to protect against data breaches and unauthorized access:

- Backend Database Protection
  - Isolate database servers from other systems and limit host connections.
  - Disable network (TCP) access when possible; use local socket files or named pipes.
  - Configure database to bind only on localhost when appropriate.
  - Restrict network port access to specific hosts with firewall rules.
  - Place database server in separate DMZ isolated from application server.
  - Never allow direct connections from thick clients to backend database.

- Transport Layer Security
  - Configure database to only allow encrypted connections.
  - Install trusted digital certificates on database servers.
  - Use TLSv1.2+ with modern ciphers (AES-GCM, ChaCha20) for client connections.
  - Verify digital certificate validity in client applications.
  - Ensure all database traffic is encrypted, not just initial authentication.

- Secure Authentication Configuration
  - Always require authentication, including from local server connections.
  - Protect accounts with strong, unique passwords.
  - Use dedicated accounts per application or service.
  - Configure minimum required permissions only.
  - Regularly review accounts and permissions.
  - Remove accounts when applications are decommissioned.
  - Change passwords when staff leave or compromise is suspected.

- Database Credential Storage
  - Never store credentials in application source code.
  - Store credentials in configuration files outside web root.
  - Set appropriate file permissions for credential access.
  - Never check credential files into source code repositories.
  - Encrypt credential storage using built-in functionality when available.
  - Use environment variables or secrets management solutions.

- Secure Permission Management
  - Apply principle of least privilege to all database accounts.
  - Do not use built-in root, sa, or SYS accounts.
  - Do not grant administrative rights to application accounts.
  - Restrict account connections to allowed hosts only.
  - Use separate databases and accounts for Development, UAT, and Production.
  - Grant only required permissions (SELECT, UPDATE, DELETE as needed).
  - Avoid making accounts database owners to prevent privilege escalation.
  - Implement table-level, column-level, and row-level permissions when needed.

- Database Configuration and Hardening
  - Install required security updates and patches regularly.
  - Run database services under low-privileged user accounts.
  - Remove default accounts and sample databases.
  - Store transaction logs on separate disk from main database files.
  - Configure regular encrypted database backups with proper permissions.
  - Disable unnecessary stored procedures and dangerous features.
  - Implement database activity monitoring and alerting.

- Platform-Specific Hardening
  - SQL Server: Disable xp_cmdshell, CLR execution, SQL Browser service, Mixed Mode Authentication (unless required).
  - MySQL/MariaDB: Run mysql_secure_installation, disable FILE privilege for users.
  - PostgreSQL: Follow PostgreSQL security documentation guidelines.
  - MongoDB: Implement MongoDB security checklist requirements.
  - Redis: Follow Redis security guide recommendations.

Summary:  
Isolate database systems, enforce encrypted connections, implement strong authentication, store credentials securely using secrets management, apply least privilege permissions, harden database configurations, and maintain regular security updates and monitoring.
