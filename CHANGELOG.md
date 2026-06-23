# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

Post-v1.0 work sitting on `main` above the pinned `v1.0` tag. Documentation, validator, and reference tooling evolve here; the shipped wordlist corpus stays frozen at `v1.0`. Per `docs/GOVERNANCE.md`, SHA-256 in each `mappings/*.json` is the load-bearing identifier for integrators.

### Structure

- All 30 non-English wordlists unified under `wordlists/tzur-original/` as index-paired semantic translations of canonical English BIP-39.
- Canonical BIP-39 wordlists from the spec preserved at `wordlists/reference-canonical/` for spec comparison; reference material, not the display source.
- Mappings at `mappings/*.json` declare `"pairing_type": "translation"` and carry a stable identifier triple `language`, `version`, `sha256`, plus `normalization_form`.

### Added

- [`docs/BIP-multilingual-mnemonics.md`](docs/BIP-multilingual-mnemonics.md). Informational BIP draft specifying the display-layer wordlist convention, MUST/SHOULD rules, input parsing, backup and portability policy, conformance profile, and security considerations.
- [`docs/V2_VALIDATION.md`](docs/V2_VALIDATION.md). v2 multi-signal validation methodology: blind LLM top-8 generation, multilingual embedding similarity (LaBSE), Wiktionary cross-reference. Per-language tier distribution and reviewer process.
- [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md). Versioning model, breaking-change policy, communication channel, change-management process for non-wordlist updates.
- [`docs/IMPLEMENTER_NOTES.md`](docs/IMPLEMENTER_NOTES.md). Non-normative wallet-side guidance for backup, restore, input handling, ZWNJ strategies, wordlist artifact governance, test fixtures.
- [`docs/COVERAGE_METHODOLOGY.md`](docs/COVERAGE_METHODOLOGY.md). Per-language calculation behind the "roughly a third / two thirds" coverage framing, with definitional choices and sensitivity range.
- [`docs/canonical-vs-tzur.md`](docs/canonical-vs-tzur.md). Word-set comparison between canonical BIP-39 and TZUR Original for the nine languages with a canonical counterpart.
- [`docs/compound-entries.md`](docs/compound-entries.md) and [`validation/compound-entries.json`](validation/compound-entries.json). Per-language dataset of entries stored as glued multi-word compounds, for downstream input-UX hints.
- [`docs/prefix-statistics.md`](docs/prefix-statistics.md) and [`validation/prefix_stats.py`](validation/prefix_stats.py). Per-language 2/3/4-character prefix uniqueness, top prefixes, and largest collision group. Quantifies the SHOULD on 4-character prefix autocomplete: uniqueness holds only for Korean, so wallets fall back to full-word matching elsewhere.
- README gains a **Manual recovery** section and `docs/IMPLEMENTER_NOTES.md` a fuller no-tooling walkthrough: converting a display backup to canonical English by index (display word -> line number -> English word at the same line), with the derivation-path and passphrase caveats.

### Changed

- v2 multi-signal sweep applied corrections across all 30 TZUR Original wordlists. Per-language counts in [`docs/V2_VALIDATION.md`](docs/V2_VALIDATION.md). Recurring patterns: glued-compound de-gluing, POS sharpening, loanword adoption, modern-vs-archaic register, polysemy-trap rejections.
- Reference decoders enforce BIP-39 checksum at the resolved English step.
- BIP draft adds homograph supply-chain section, discovery framing, portability SHOULDs.
- Encoding notes corrected on ZWNJ behavior under NFKD (preserved, not stripped).
- BIP draft Input parsing adds a normalization-ambiguity MUST: a wallet that applies a lossy fold (diacritic stripping, case folding) and finds a token matching more than one entry MUST reject and ask the user to disambiguate, never silently pick one. Motivation notes English's broader wallet support; Backwards Compatibility states the checksum is preserved because indices are preserved; Coexistence adds an interoperability SHOULD preferring the display path over new legacy non-English backups (without deprecating legacy lists or existing backups).
- README and `validation/encoding-notes.md` document the same normalization-ambiguity rule and the checksum-preservation rationale.

### Validation

- `validation/validate_all.py` extends NFC-at-rest enforcement to mappings, test vectors, and compound entries. Embedded whitespace is checked under the full Unicode `White_Space` property. Validator verifies the `sha256` field in each mapping matches the corresponding wordlist file byte-for-byte.
- All 30 wordlists pass `validation/validate_all.py` on every push (CI-enforced). The English cryptographic floor is unchanged: a seed produced under any TZUR Original wordlist derives bit-identical keys to the equivalent English phrase.
- `validation/validate_all.py` adds a normalization-collision check per TZUR Original wordlist. NFKD collisions (the BIP-39 PBKDF2 normalization) are a hard error and are zero across all 30 lists. Diacritic-fold and case-fold collisions are reported as warnings, flagging the languages where a wallet must not silently strip accents or case on input (Vietnamese 85, Thai 46, Swedish 17, and others).

## [1.0] - 2026-04-18

First public release. The `v1.0` tag was last moved on 2026-04-22 to pin a Romanian wordlist sync; under the current pinned-tag policy in `docs/GOVERNANCE.md`, the tag stays anchored at the shipped commit going forward. SHA-256 in each `mappings/*.json` remains the load-bearing identifier for any consumer detecting change.

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
