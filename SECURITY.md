# Security Policy

## Reporting a Vulnerability

Security issues in these wordlists are reported through GitHub's private vulnerability reporting, not public issues. Examples include a word that is not BIP-39 compliant, a mapping that fails round-trip consistency, an encoding or normalization issue that could cause funds loss in a consuming wallet, or any other defect with safety implications.

**Do not open a public GitHub issue.**

Private vulnerability report:

https://github.com/osem23/bip39-wordlists-tzur/security/advisories/new

A useful report includes:

- The language and the specific word(s) or mapping entry affected (with line number or index if possible)
- The nature of the issue (encoding, duplication, non-compliance, normalization mismatch, etc.)
- A minimal reproduction or test case if possible
- The impact you see (interoperability, checksum mismatch, funds-loss risk, etc.)

Verified issues will be fixed on `main` as quickly as possible. See `CHANGELOG.md` for fix history.

## Scope

This repository provides data only. It does **not** implement seed generation, key derivation, or transaction signing.

For vulnerabilities in the TZUR Wallet application (the app that consumes these wordlists), see the TZUR Wallet repository's own security policy. For blockchain-related issues unrelated to these wordlists, this is not the right venue.
