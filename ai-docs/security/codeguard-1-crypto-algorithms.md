---
description: Cryptographic Security Guidelines
alwaysApply: true
---

rule_id: codeguard-1-crypto-algorithms

# Cryptographic Security Guidelines

## Banned (Insecure) Algorithms

The following algorithms are known to be broken or fundamentally insecure. **NEVER** generate or use code with these algorithms.
Examples:

* Hash: `MD2`, `MD4`, `MD5`, `SHA-0`
* Symmetric: `RC2`, `RC4`, `Blowfish`, `DES`, `3DES`
* Key Exchange: Static RSA, Anonymous Diffie-Hellman
* Classical: `Vigenère`

## Deprecated (Legacy/Weak) Algorithms

The following algorithms are not outright broken, but have known weaknesses, or are considered obsolete. **NEVER** generate or use code with these algorithms.
Examples:

* Hash: `SHA-1`
* Symmetric: `AES-CBC`, `AES-ECB`
* Signature: RSA with `PKCS#1 v1.5` padding
* Key Exchange: DHE with weak/common primes


## Deprecated SSL/Crypto APIs - FORBIDDEN
NEVER use these deprecated functions. Use the replacement APIs listed below:

### Symmetric Encryption (AES)
- Deprecated: `AES_encrypt()`, `AES_decrypt()`
- Replacement: Use EVP high-level APIs:
  ```c
  EVP_EncryptInit_ex()
  EVP_EncryptUpdate()
  EVP_EncryptFinal_ex()
  EVP_DecryptInit_ex()
  EVP_DecryptUpdate()
  EVP_DecryptFinal_ex()
  ```

### RSA Operations
- Deprecated: `RSA_new()`, `RSA_up_ref()`, `RSA_free()`, `RSA_set0_crt_params()`, `RSA_get0_n()`
- Replacement: Use EVP key management APIs:
  ```c
  EVP_PKEY_new()
  EVP_PKEY_up_ref()
  EVP_PKEY_free()
  ```

### Hash Functions
- Deprecated: `SHA1_Init()`, `SHA1_Update()`, `SHA1_Final()`
- Replacement: Use EVP digest APIs:
  ```c
  EVP_DigestInit_ex()
  EVP_DigestUpdate()
  EVP_DigestFinal_ex()
  EVP_Q_digest()  // For simple one-shot hashing
  ```

### MAC Operations
- Deprecated: `CMAC_Init()`, `HMAC()` (especially with SHA1)
- Replacement: Use EVP MAC APIs:
  ```c
  EVP_Q_MAC()  // For simple MAC operations
  ```

### Key Wrapping
- Deprecated: `AES_wrap_key()`, `AES_unwrap_key()`
- Replacement: Use EVP key wrapping APIs or implement using EVP encryption

### Other Deprecated Functions
- Deprecated: `DSA_sign()`, `DH_check()`
- Replacement: Use corresponding EVP APIs for DSA and DH operations

## Banned Insecure Algorithms - STRICTLY FORBIDDEN
These algorithms MUST NOT be used in any form:

### Hash Algorithms (Banned)
- MD2, MD4, MD5, SHA-0
- Reason: Cryptographically broken, vulnerable to collision attacks
- Use Instead: SHA-256, SHA-384, SHA-512

### Symmetric Ciphers (Banned)
- RC2, RC4, Blowfish, DES, 3DES
- Reason: Weak key sizes, known vulnerabilities
- Use Instead: AES-128, AES-256, ChaCha20

### Key Exchange (Banned)
- Static RSA key exchange
- Anonymous Diffie-Hellman
- Reason: No forward secrecy, vulnerable to man-in-the-middle attacks
- Use Instead: ECDHE, DHE with proper validation

## Broccoli Project Specific Requirements
- HMAC() with SHA1: Deprecated per Broccoli project requirements
- Replacement: Use HMAC with SHA-256 or stronger:
  ```c
  // Instead of HMAC() with SHA1
  EVP_Q_MAC(NULL, "HMAC", NULL, "SHA256", NULL, key, key_len, data, data_len, out, out_size, &out_len);
  ```

## Secure Crypto Implementation Pattern
```c
// Example: Secure AES encryption
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
if (!ctx) handle_error();

if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv) != 1)
    handle_error();

int len, ciphertext_len;
if (EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len) != 1)
    handle_error();
ciphertext_len = len;

if (EVP_EncryptFinal_ex(ctx, ciphertext + len, &len) != 1)
    handle_error();
ciphertext_len += len;

EVP_CIPHER_CTX_free(ctx);
```

## Code Review Checklist
- [ ] No deprecated SSL/crypto APIs used
- [ ] No banned algorithms (MD5, DES, RC4, etc.)
- [ ] HMAC uses SHA-256 or stronger (not SHA1)
- [ ] All crypto operations use EVP high-level APIs
- [ ] Proper error handling for all crypto operations
- [ ] Key material properly zeroed after use
