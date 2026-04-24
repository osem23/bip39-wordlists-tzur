# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Unified display wordlists at 30 TZUR Original index-paired translations. Tag `v1.0` remains pinned to its original commit; these changes sit on `main` above the tag.

### Structure

- All 30 non-English wordlists under `wordlists/tzur-original/` are index-paired semantic translations of canonical English BIP-39.
- Canonical BIP-39 wordlists from the spec are preserved at `wordlists/reference-canonical/` for comparison. They are reference material, not the display source.
- Mappings at `mappings/*.json` declare `"pairing_type": "translation"`.

### Added

- [`docs/canonical-vs-tzur.md`](docs/canonical-vs-tzur.md). Word-set comparison between canonical BIP-39 and TZUR Original for the nine languages with a canonical counterpart.
- [`docs/compound-entries.md`](docs/compound-entries.md) and [`validation/compound-entries.json`](validation/compound-entries.json). Per-language dataset of entries stored as glued multi-word compounds, for downstream input-UX hints.

### Validation

All 30 wordlists pass `validation/validate_all.py`: 2048 entries, UTF-8 without BOM, no duplicates, no whitespace, no hyphen or space within a word, bidirectional mapping round-trip consistent. The English cryptographic floor is unchanged. A seed produced under any TZUR Original wordlist derives bit-identical keys to the equivalent English phrase.

## [1.0] - 2026-04-18

First public release.

### Summary

BIP-39 compliant wordlists and bidirectional English-to-native mappings for **31 languages**, all strictly validated (2048 words, no duplicates, UTF-8, no BOM, no whitespace, round-trip consistent). The English wordlist works with any BIP-39 wallet; the 30 native-language wordlists currently work with TZUR Wallet and become cross-wallet portable as other wallets integrate them.

### Wordlist inventory

**TZUR Original (20).** Built from scratch by [osem23](https://github.com/osem23):

- **15 with no prior BIP-39 wordlist known at publication**: Arabic, Bengali, Danish, Estonian, Farsi, Filipino, Hebrew, Malay, Polish, Romanian, Swedish, Thai, Ukrainian, Urdu, Vietnamese.
- **5 independently curated** (prior BIP-39 lists exist from other projects; ours were created independently): Dutch, German, Indonesian, Russian, Turkish.

**Community (1).** Hindi, derived from [`devnagri_wordlist`](https://github.com/ujjwali2s/devnagri_wordlist) (98% ordinal match, attribution verified).

**Official BIP-39 (10).** Included for completeness with bidirectional mappings; not our work: Chinese (Simplified), Chinese (Traditional), Czech, English, French, Italian, Japanese, Korean, Portuguese, Spanish.

### Included

- 31 wordlists under `wordlists/` (`official-bip39/`, `community/`, `tzur-original/`).
- 30 bidirectional mapping files under `mappings/` (English is the reference language).
- Automated validation at `validation/validate_all.py` covering word count, duplicates, encoding, whitespace, and mapping round-trip integrity.
- Encoding and NFKD normalization guidance at `validation/encoding-notes.md`, including ZWNJ handling for Farsi.
- Checksum test vectors at `validation/checksum-tests.json`.

### Notes

- 4-char prefix uniqueness is not guaranteed for TZUR Original wordlists. Implementations relying on 4-char autocomplete should fall back to full-word matching.
- This repository does not implement a wallet and does not generate seeds, derive keys, or sign transactions. See `DISCLAIMER.md`.

[1.0]: https://github.com/osem23/bip39-wordlists-tzur/releases/tag/v1.0
