# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased — 2026-04-21

Unified display wordlists at 30 TZUR Original translations. Tag `v1.0.0` remains pinned to its original commit; these changes sit on `main` above the tag.

### Changed

- The 10 languages previously served by canonical BIP-39 wordlists (Spanish, French, Italian, Portuguese, Czech, Japanese, Korean, Simplified Chinese, Traditional Chinese) and the 1 community Hindi wordlist are replaced by TZUR Original index-paired translations. All 30 non-English wordlists under `wordlists/tzur-original/` now follow the same index-paired translation model: the native word at index N is a semantic translation of the canonical English word at index N.
- The canonical BIP-39 wordlists from the spec are preserved at `wordlists/reference-canonical/` (renamed from `wordlists/official-bip39/`) for spec comparison. They are no longer the display source; they are reference material.
- Mappings at `mappings/*.json` now all declare `"pairing_type": "translation"`. All 30 mapping files are index-paired translations.
- `wordlists/community/` removed. The former community Hindi list was superseded by a full TZUR Original Hindi translation.

### Added

- `docs/canonical-vs-tzur.md`. Per-language side-by-side diff showing how many positions differ between the canonical BIP-39 wordlist and the TZUR Original translation, with the first 30 entries for each of the 9 languages that have a canonical counterpart.
- Back-translation and LLM-verdict audit applied to 9 of the 10 new TZUR Originals (Spanish, French, Italian, Portuguese, Japanese, Korean, Simplified Chinese, Traditional Chinese, Hindi). Czech is the tenth; its translation-accuracy audit is scheduled as a follow-up pass.

### Structural

- All 30 wordlists pass `validation/validate_all.py`: 2048 entries each, UTF-8 without BOM, no duplicates, no whitespace, bidirectional mapping round-trip consistent.
- The English cryptographic floor is unchanged. A seed produced under any TZUR Original wordlist derives bit-identical keys to the equivalent English phrase.

### Seeds generated against the former Hindi list

The previous Hindi list was sourced from `devnagri_wordlist` with attribution. Seeds generated against that list in any prior-state wallet remain restorable via the English form, which is unchanged. The current Hindi TZUR Original replaces the community list in this repository; wallets that want Hindi-to-Hindi restore paths across both versions should keep both mappings on hand.

## [1.0.0] - 2026-04-18

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

[1.0.0]: https://github.com/osem23/bip39-wordlists-tzur/releases/tag/v1.0.0
