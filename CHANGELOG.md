# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-18

First public release.

### Summary

BIP-39 compliant wordlists and bidirectional English-to-native mappings for **31 languages**, all strictly validated (2048 words, no duplicates, UTF-8, no BOM, no whitespace, round-trip consistent). Works with any BIP-39 wallet across any cryptocurrency.

### Wordlist inventory

**TZUR Original (20)** — built from scratch by the TZUR team:

- **15 first-known** (no prior BIP-39 wordlist existed before this work): Arabic, Bengali, Danish, Estonian, Farsi, Filipino, Hebrew, Malay, Polish, Romanian, Swedish, Thai, Ukrainian, Urdu, Vietnamese.
- **5 independently curated** (prior BIP-39 lists exist from other projects; ours were created independently): Dutch, German, Indonesian, Russian, Turkish.

**Community (1)** — Hindi, derived from [`devnagri_wordlist`](https://github.com/ujjwali2s/devnagri_wordlist) (98% ordinal match, attribution verified).

**Official BIP-39 (10)** — included for completeness with bidirectional mappings; not our work: Chinese (Simplified), Chinese (Traditional), Czech, English, French, Italian, Japanese, Korean, Portuguese, Spanish.

### Included

- 31 wordlists under `wordlists/` (`official-bip39/`, `community/`, `tzur-original/`).
- 30 bidirectional mapping files under `mappings/` (English is the reference language).
- Automated validation at `validation/validate_all.py` covering word count, duplicates, encoding, whitespace, and mapping round-trip integrity.
- Encoding and NFKD normalization guidance at `validation/encoding-notes.md`, including ZWNJ handling for Farsi.
- Checksum test vectors at `validation/checksum-tests.json`.

### Notes

- 4-char prefix uniqueness is not guaranteed for TZUR Original wordlists. Implementations relying on 4-char autocomplete should fall back to full-word matching.
- This repository does not implement a wallet and does not generate seeds, derive keys, or sign transactions. See `DISCLAIMER.md`.

[1.0.0]: https://github.com/osem23/bip39-wordlists-tzur/releases/tag/v1.0.0
