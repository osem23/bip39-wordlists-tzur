# BIP-39 Wordlists. TZUR Originals.

Index-paired, audited, multi-script display wordlists for BIP-39 mnemonics in 30 languages.

[![Validate](https://github.com/osem23/bip39-wordlists-tzur/actions/workflows/validate.yml/badge.svg)](https://github.com/osem23/bip39-wordlists-tzur/actions/workflows/validate.yml)
![Languages](https://img.shields.io/badge/Languages-30-blue)
![Entries audited](https://img.shields.io/badge/Entries%20audited-61%2C440-blue)
![Refinements applied](https://img.shields.io/badge/Refinements%20applied-2%2C405-blue)
![Known errors post-audit](https://img.shields.io/badge/Known%20errors%20post--audit-0-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Tag](https://img.shields.io/badge/Tag-v1.0-informational)

## Overview

This repository publishes 30 TZUR Original BIP-39 display wordlists in non-English languages, each index-paired to the canonical English BIP-39 wordlist. The 10 canonical BIP-39 wordlists from the spec are preserved at [`wordlists/reference-canonical/`](wordlists/reference-canonical/) for reference. Seeds commit to canonical English; PBKDF2 derivation runs on the English form, so native-language wordlists are a display and input layer with no new cryptographic surface.

Built by [osem23](https://github.com/osem23), builder of [TZUR Wallet](https://tzur.live) and founder of [BlockSight.Live](https://blocksight.live). TZUR Wallet ships these wordlists to iOS; any BIP-39 wallet can integrate them using the bidirectional mappings in [`mappings/`](mappings/).

## Why this exists

**The language coverage gap.** BIP-39 ships canonical wordlists for 10 languages (English plus Spanish, French, Italian, Portuguese, Czech, Japanese, Korean, Simplified Chinese, Traditional Chinese). Those 10 cover roughly 35% of humanity by native language. The remaining 65%, around 5 billion people, have no canonical BIP-39 wordlist in their native language. They either work in English or don't use Bitcoin at all. Estimates drawn from Ethnologue 2024 language-speaker totals. This repository extends first-class display-layer coverage to 30 languages, adding Arabic, Hindi, Bengali, Urdu, Farsi, Turkish, Vietnamese, Thai, Hebrew, Polish, Ukrainian, Romanian, Swedish, Danish, Filipino, Malay, Indonesian, Russian, Dutch, German, and Estonian. For 15 of those no prior BIP-39 wordlist was known to exist at time of publication.

**The translation gap.** The 9 non-English canonical BIP-39 wordlists are **not translations of the English list**. They are independent wordlists in each language, selected for 4-char prefix uniqueness and common vocabulary, then alphabetized by native-script collation. That is a valid design choice and the spec is explicit about it for readers who look closely. In practice most readers do not, and reasonably assume the Spanish word at index 5 is the Spanish translation of the English word at index 5. It is not. At most indices the two have no semantic relationship at all.

The data makes the gap explicit (per-language numbers in [`docs/canonical-vs-tzur.md`](docs/canonical-vs-tzur.md)):

| Language | Shared tokens between canonical and TZUR Original |
|---|---:|
| Korean | 0 of 2048 |
| Japanese | 11 of 2048 |
| Chinese (Traditional) | 45 of 2048 |
| Chinese (Simplified) | 75 of 2048 |
| Czech | 303 of 2048 |
| Italian | 430 of 2048 |
| Portuguese | 423 of 2048 |
| French | 495 of 2048 |
| Spanish | 705 of 2048 |

Korean is the clean case: the canonical spec list and a semantic translation share zero tokens. Japanese, Chinese, and the Latin-script languages land where you would expect from independent common-word sampling.

This repository implements the display-layer convention explicitly: the native word at index N is a semantic translation of the English word at index N. Seeds still commit to canonical English; PBKDF2 still runs on the English form. Native-language wordlists are a UX layer over that cryptographic floor, not a parallel cryptographic artifact. The canonical non-English wordlists are preserved at [`wordlists/reference-canonical/`](wordlists/reference-canonical/) so anyone who needs to cite or compare against the spec can do so.

## Informational BIP Proposal

> This repository is the reference implementation for [`docs/BIP-multilingual-mnemonics.md`](docs/BIP-multilingual-mnemonics.md), an Informational BIP draft specifying the native-language display wordlist convention. The seed of record remains the canonical English mnemonic. Display wordlists are a UX layer with no new cryptographic surface. The draft defines MUST/SHOULD rules for wordlist structure, input parsing, test vectors, and security considerations.

## Audit and Validation

Every TZUR Original wordlist passes three validation layers. Aggregate: 61,440 entries audited (30 languages × 2048). 1,450 entries flagged WRONG by translation-accuracy verdicts and replaced. An additional script-normalization pass against the Traditional Chinese wordlist replaced 955 simplified-character entries with their Traditional-character equivalents. Total refinements: 2,405. Post-fix known error rate: 0% against every completed audit layer for every language.

Method:

- **Layer 1. Structural validation.** Exactly 2048 entries, UTF-8 without BOM, no duplicates, no whitespace, Unix line endings, bijective mapping round-trip.
- **Layer 2. Back-translation pass.** Each native word is back-translated to English via Google Translate. Divergences are flagged as suspects. An LLM verdict agent compares native directly to English and replaces WRONG entries.
- **Layer 3. Forward-translation pass.** Each English word is forward-translated to the native language via Microsoft Azure Translator. Same LLM verdict layer. Catches false friends, homonym sense-shifts, and cases back-translation would miss.

Per-language status:

| Language | Structural | Back-translation | Forward-translation | Refinements | Native-speaker review |
|---|---|---|---|---:|---|
| Arabic | Clean | Complete | Complete | 4 | Pending |
| Bengali | Clean | Complete | Complete | 0 | Pending |
| Chinese (Simplified) | Clean | Complete | Complete | 86 | Pending |
| Chinese (Traditional) | Clean | Complete | Complete | 1,037 | Pending |
| Czech | Clean | Complete | Complete | 625 | Pending |
| Danish | Clean | Complete | Complete | 0 | Pending |
| Dutch | Clean | Complete | Complete | 1 | Pending |
| Estonian | Clean | Complete | Complete | 36 | Pending |
| Farsi | Clean | Complete | Complete | 0 | Pending |
| Filipino | Clean | Complete | Complete | 23 | Pending |
| French | Clean | Complete | Complete | 2 | Pending |
| German | Clean | Complete | Complete | 1 | Pending |
| **Hebrew** | Clean | Complete | Complete | 5 | **Complete (native he)** |
| Hindi | Clean | Complete | Complete | 181 | Pending |
| Indonesian | Clean | Complete | Complete | 9 | Pending |
| Italian | Clean | Complete | Complete | 49 | Pending |
| Japanese | Clean | Complete | Complete | 42 | Pending |
| Korean | Clean | Complete | Complete | 43 | Pending |
| Malay | Clean | Complete | Complete | 3 | Pending |
| Polish | Clean | Complete | Complete | 4 | Pending |
| **Portuguese** | Clean | Complete | Complete | 3 | **Peer-reviewed (native pt-BR)** |
| Romanian | Clean | Complete | Complete | 0 | Pending |
| Russian | Clean | Complete | Complete | 4 | Pending |
| **Spanish** | Clean | Complete | Complete | 109 | **Peer-reviewed (native es-AR)** |
| Swedish | Clean | Complete | Complete | 0 | Pending |
| Thai | Clean | Complete | Complete | 3 | Pending |
| Turkish | Clean | Complete | Complete | 24 | Pending |
| Ukrainian | Clean | Complete | Complete | 35 | Pending |
| Urdu | Clean | Complete | Complete | 63 | Pending |
| Vietnamese | Clean | Complete | Complete | 13 | Pending |

Full methodology, per-language construction notes, and reproducibility statement live at [`docs/CONSTRUCTION.md`](docs/CONSTRUCTION.md). Translation-engine validation is not a substitute for native-speaker review. Hebrew, Spanish, and Portuguese carry native-speaker signals today; the other 27 have the three-layer translation-accuracy audit above and are pending native review. Contributions land via issues and PRs and are acknowledged in the matrix as they arrive.

## Wordlists and Mappings

30 TZUR Original display wordlists at [`wordlists/tzur-original/`](wordlists/tzur-original/). 10 canonical BIP-39 wordlists preserved at [`wordlists/reference-canonical/`](wordlists/reference-canonical/) for spec comparison. Each TZUR Original is accompanied by a bidirectional JSON mapping at [`mappings/`](mappings/).

| Language | Wordlist | Mapping | Script | Prior BIP-39 list |
|----------|----------|---------|--------|--------|
| Arabic | [`arabic.txt`](wordlists/tzur-original/arabic.txt) | [`arabic.json`](mappings/arabic.json) | Arabic | None known |
| Bengali | [`bengali.txt`](wordlists/tzur-original/bengali.txt) | [`bengali.json`](mappings/bengali.json) | Bengali | None known |
| Chinese (Simplified) | [`chinese_simplified.txt`](wordlists/tzur-original/chinese_simplified.txt) | [`chinese_simplified.json`](mappings/chinese_simplified.json) | Han (Simplified) | Canonical spec |
| Chinese (Traditional) | [`chinese_traditional.txt`](wordlists/tzur-original/chinese_traditional.txt) | [`chinese_traditional.json`](mappings/chinese_traditional.json) | Han (Traditional) | Canonical spec |
| Czech | [`czech.txt`](wordlists/tzur-original/czech.txt) | [`czech.json`](mappings/czech.json) | Latin (with diacritics) | Canonical spec |
| Danish | [`danish.txt`](wordlists/tzur-original/danish.txt) | [`danish.json`](mappings/danish.json) | Latin (with æ ø å) | None known |
| Dutch | [`dutch.txt`](wordlists/tzur-original/dutch.txt) | [`dutch.json`](mappings/dutch.json) | Latin | Independent prior lists |
| Estonian | [`estonian.txt`](wordlists/tzur-original/estonian.txt) | [`estonian.json`](mappings/estonian.json) | Latin (with ä ö ü õ) | None known |
| Farsi | [`farsi.txt`](wordlists/tzur-original/farsi.txt) | [`farsi.json`](mappings/farsi.json) | Arabic (with پ چ ژ گ) | None known |
| Filipino | [`filipino.txt`](wordlists/tzur-original/filipino.txt) | [`filipino.json`](mappings/filipino.json) | Latin | None known |
| French | [`french.txt`](wordlists/tzur-original/french.txt) | [`french.json`](mappings/french.json) | Latin | Canonical spec |
| German | [`german.txt`](wordlists/tzur-original/german.txt) | [`german.json`](mappings/german.json) | Latin (with ä ö ü ß) | Independent prior lists |
| Hebrew | [`hebrew.txt`](wordlists/tzur-original/hebrew.txt) | [`hebrew.json`](mappings/hebrew.json) | Hebrew | None known |
| Hindi | [`hindi.txt`](wordlists/tzur-original/hindi.txt) | [`hindi.json`](mappings/hindi.json) | Devanagari | Prior community list (superseded) |
| Indonesian | [`indonesian.txt`](wordlists/tzur-original/indonesian.txt) | [`indonesian.json`](mappings/indonesian.json) | Latin | Independent prior lists |
| Italian | [`italian.txt`](wordlists/tzur-original/italian.txt) | [`italian.json`](mappings/italian.json) | Latin | Canonical spec |
| Japanese | [`japanese.txt`](wordlists/tzur-original/japanese.txt) | [`japanese.json`](mappings/japanese.json) | Kanji + Kana | Canonical spec |
| Korean | [`korean.txt`](wordlists/tzur-original/korean.txt) | [`korean.json`](mappings/korean.json) | Hangul | Canonical spec |
| Malay | [`malay.txt`](wordlists/tzur-original/malay.txt) | [`malay.json`](mappings/malay.json) | Latin | None known |
| Polish | [`polish.txt`](wordlists/tzur-original/polish.txt) | [`polish.json`](mappings/polish.json) | Latin (with ą ć ę ł ń ó ś ź ż) | None known |
| Portuguese | [`portuguese.txt`](wordlists/tzur-original/portuguese.txt) | [`portuguese.json`](mappings/portuguese.json) | Latin | Canonical spec |
| Romanian | [`romanian.txt`](wordlists/tzur-original/romanian.txt) | [`romanian.json`](mappings/romanian.json) | Latin (with ă â î ș ț) | None known |
| Russian | [`russian.txt`](wordlists/tzur-original/russian.txt) | [`russian.json`](mappings/russian.json) | Cyrillic | Independent prior lists |
| Spanish | [`spanish.txt`](wordlists/tzur-original/spanish.txt) | [`spanish.json`](mappings/spanish.json) | Latin | Canonical spec |
| Swedish | [`swedish.txt`](wordlists/tzur-original/swedish.txt) | [`swedish.json`](mappings/swedish.json) | Latin (with å ä ö) | None known |
| Thai | [`thai.txt`](wordlists/tzur-original/thai.txt) | [`thai.json`](mappings/thai.json) | Thai | None known |
| Turkish | [`turkish.txt`](wordlists/tzur-original/turkish.txt) | [`turkish.json`](mappings/turkish.json) | Latin (with ç ğ ı ö ş ü) | Independent prior lists |
| Ukrainian | [`ukrainian.txt`](wordlists/tzur-original/ukrainian.txt) | [`ukrainian.json`](mappings/ukrainian.json) | Cyrillic (with ї є і ґ) | None known |
| Urdu | [`urdu.txt`](wordlists/tzur-original/urdu.txt) | [`urdu.json`](mappings/urdu.json) | Perso-Arabic RTL | None known |
| Vietnamese | [`vietnamese.txt`](wordlists/tzur-original/vietnamese.txt) | [`vietnamese.json`](mappings/vietnamese.json) | Latin (with diacritics) | None known |

"Prior BIP-39 list" records whether a pre-existing BIP-39 wordlist existed in that language before this repository. `Canonical spec` means the BIP-39 specification itself ships a canonical wordlist (alphabetized independent selection, not translation); it is preserved at [`wordlists/reference-canonical/`](wordlists/reference-canonical/). `None known` is a best-effort claim at time of publication. See [`docs/canonical-vs-tzur.md`](docs/canonical-vs-tzur.md) for the word-set overlap between canonical and TZUR Original for the nine languages with a canonical counterpart.

## Usage

Load a wordlist by position, or load a mapping for bidirectional native-English translation.

```python
words = open("wordlists/tzur-original/hebrew.txt").read().strip().split("\n")
assert len(words) == 2048
mnemonic_word = words[entropy_bits]
```

```python
import json
mapping = json.load(open("mappings/hebrew.json"))
hebrew_word = mapping["english_to_native"]["abandon"]  # "נטוש"
english_word = mapping["native_to_english"]["נטוש"]    # "abandon"
```

```javascript
const mapping = require('./mappings/hebrew.json');
const hebrewWord = mapping.english_to_native['abandon']; // "נטוש"
const englishWord = mapping.native_to_english['נטוש'];   // "abandon"
```

Each mapping file contains `language`, `word_count`, `description`, `pairing_type`, `english_to_native`, `native_to_english`. `pairing_type: "translation"` for all 30 TZUR Original mappings.

## Design and BIP-39 Compliance

- Exactly 2048 entries per wordlist, one per line, UTF-8 without BOM, Unix line endings.
- No duplicates. No leading or trailing whitespace on any line.
- Deterministic bijective mapping, round-trip verified against English at every index.
- Normalization: NFC at rest, NFKD before PBKDF2 as required by BIP-39. See [`validation/encoding-notes.md`](validation/encoding-notes.md).
- 4-char prefix uniqueness is not guaranteed across all scripts. Wallets relying on prefix autocomplete should fall back to full-word matching.
- Run [`validation/validate_all.py`](validation/validate_all.py) to re-verify every wordlist and mapping.

## Remaining Limitations

- Native-speaker review pending for 27 of 30 languages. Hebrew has full review; Spanish and Portuguese are peer-reviewed by native speakers. The other 27 carry the three-layer translation-accuracy audit above but not yet native-speaker validation.
- "No prior known wordlist" for 15 languages is a best-effort claim at time of publication. If a pre-existing wordlist surfaces, it will be acknowledged.
- No external cryptographic or linguistic audit has been performed. Independent review is welcome via PR.

## Documentation

- [`docs/BIP-multilingual-mnemonics.md`](docs/BIP-multilingual-mnemonics.md). Informational BIP draft specifying the display-layer wordlist convention: MUST/SHOULD rules, input parsing, test vectors, security considerations.
- [`docs/CONSTRUCTION.md`](docs/CONSTRUCTION.md). Construction methodology, disambiguation rules, per-language construction notes, review status matrix, reproducibility statement.
- [`docs/canonical-vs-tzur.md`](docs/canonical-vs-tzur.md). Word-set difference between canonical BIP-39 and TZUR Original for the nine languages with a canonical counterpart.
- [`validation/encoding-notes.md`](validation/encoding-notes.md). UTF-8, NFKD normalization, ZWNJ handling for Farsi, per-language normalization impact.
- [`test-vectors/`](test-vectors/). BIP-39 conformance vectors per language. Integrators reproduce every vector in the target language before shipping.
- [`examples/`](examples/). Reference decoders in Python, JavaScript, and Swift. Byte-identical seeds across all three.

## Security

This repository contains reference data only. It does not implement a wallet, generate seeds, derive keys, or sign transactions. Use at your own risk. Report security issues via GitHub's private vulnerability reporting; see [`SECURITY.md`](SECURITY.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Corrections, native-speaker reviews, and new languages land via issues and PRs.

## License

[MIT](LICENSE)

---

Maintained by [osem23](https://github.com/osem23). Builder of [TZUR Wallet](https://tzur.live). Founder of [BlockSight.Live](https://blocksight.live).
