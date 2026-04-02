# BIP-39 Wordlists

> Most Bitcoin wallets only support seed phrases in English. This repository provides BIP-39 compliant wordlists in 22 languages, including 7 languages (Arabic, Farsi, Filipino, Hebrew, Malay, Thai, Vietnamese) that had no known BIP-39 wordlists before this work. Built and maintained by the team behind [TZUR Wallet](https://tzur.live).

Strict, deterministic BIP-39 wordlists and bidirectional mappings for 22 languages.

Each wordlist contains exactly 2048 words, one per line, UTF-8 encoded. Each mapping provides a bidirectional English-to-native lookup, ready for use in any BIP-39 compliant wallet.

## Contents

### Wordlists

This repository contains three categories of wordlists:

#### TZUR Original Wordlists

These wordlists were created from scratch by the TZUR Wallet team. To our knowledge, no prior BIP-39 compliant wordlists existed for these languages before this work.

| Language | Wordlist | Mapping | Script |
|----------|----------|---------|--------|
| Arabic | [`wordlists/tzur-original/arabic.txt`](wordlists/tzur-original/arabic.txt) | [`mappings/arabic.json`](mappings/arabic.json) | Arabic |
| **Farsi (Persian)** | [`wordlists/tzur-original/farsi.txt`](wordlists/tzur-original/farsi.txt) | [`mappings/farsi.json`](mappings/farsi.json) | Arabic (with پ چ ژ گ) |
| Filipino | [`wordlists/tzur-original/filipino.txt`](wordlists/tzur-original/filipino.txt) | [`mappings/filipino.json`](mappings/filipino.json) | Latin |
| Hebrew | [`wordlists/tzur-original/hebrew.txt`](wordlists/tzur-original/hebrew.txt) | [`mappings/hebrew.json`](mappings/hebrew.json) | Hebrew |
| Malay | [`wordlists/tzur-original/malay.txt`](wordlists/tzur-original/malay.txt) | [`mappings/malay.json`](mappings/malay.json) | Latin |
| Thai | [`wordlists/tzur-original/thai.txt`](wordlists/tzur-original/thai.txt) | [`mappings/thai.json`](mappings/thai.json) | Thai |
| Vietnamese | [`wordlists/tzur-original/vietnamese.txt`](wordlists/tzur-original/vietnamese.txt) | [`mappings/vietnamese.json`](mappings/vietnamese.json) | Latin (with diacritics) |

#### Community Wordlists

Wordlists assembled during development, sourced or adapted from community contributions. Attribution is noted where applicable.

| Language | Wordlist | Mapping | Notes |
|----------|----------|---------|-------|
| Dutch | [`wordlists/community/dutch.txt`](wordlists/community/dutch.txt) | [`mappings/dutch.json`](mappings/dutch.json) | Based on [OpenTaal BIP-39](https://github.com/OpenTaal/opentaal-bip39) |
| German | [`wordlists/community/german.txt`](wordlists/community/german.txt) | [`mappings/german.json`](mappings/german.json) | |
| Hindi | [`wordlists/community/hindi.txt`](wordlists/community/hindi.txt) | [`mappings/hindi.json`](mappings/hindi.json) | Based on [devnagri_wordlist](https://github.com/ujjwali2s/devnagri_wordlist) |
| Indonesian | [`wordlists/community/indonesian.txt`](wordlists/community/indonesian.txt) | [`mappings/indonesian.json`](mappings/indonesian.json) | Based on [perl-WordList-ID-BIP39](https://github.com/perlancar/perl-WordList-ID-BIP39) |
| Russian | [`wordlists/community/russian.txt`](wordlists/community/russian.txt) | [`mappings/russian.json`](mappings/russian.json) | |
| Turkish | [`wordlists/community/turkish.txt`](wordlists/community/turkish.txt) | [`mappings/turkish.json`](mappings/turkish.json) | |

#### Official BIP-39 Wordlists

Standard wordlists from the [BIP-39 specification](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki). Included here for completeness with mappings. These wordlists are not our work.

| Language | Wordlist | Mapping |
|----------|----------|---------|
| Chinese (Simplified) | [`wordlists/official-bip39/chinese_simplified.txt`](wordlists/official-bip39/chinese_simplified.txt) | [`mappings/chinese_simplified.json`](mappings/chinese_simplified.json) |
| Chinese (Traditional) | [`wordlists/official-bip39/chinese_traditional.txt`](wordlists/official-bip39/chinese_traditional.txt) | [`mappings/chinese_traditional.json`](mappings/chinese_traditional.json) |
| English | [`wordlists/official-bip39/english.txt`](wordlists/official-bip39/english.txt) | - (reference language) |
| French | [`wordlists/official-bip39/french.txt`](wordlists/official-bip39/french.txt) | [`mappings/french.json`](mappings/french.json) |
| Italian | [`wordlists/official-bip39/italian.txt`](wordlists/official-bip39/italian.txt) | [`mappings/italian.json`](mappings/italian.json) |
| Japanese | [`wordlists/official-bip39/japanese.txt`](wordlists/official-bip39/japanese.txt) | [`mappings/japanese.json`](mappings/japanese.json) |
| Korean | [`wordlists/official-bip39/korean.txt`](wordlists/official-bip39/korean.txt) | [`mappings/korean.json`](mappings/korean.json) |
| Portuguese | [`wordlists/official-bip39/portuguese.txt`](wordlists/official-bip39/portuguese.txt) | [`mappings/portuguese.json`](mappings/portuguese.json) |
| Spanish | [`wordlists/official-bip39/spanish.txt`](wordlists/official-bip39/spanish.txt) | [`mappings/spanish.json`](mappings/spanish.json) |

### Mappings

The `mappings/` directory contains bidirectional English-to-native JSON mapping files for all 21 non-English languages. Each mapping file includes:

```json
{
  "language": "hebrew",
  "word_count": 2048,
  "description": "Bidirectional BIP-39 mapping between English and Hebrew",
  "english_to_native": {
    "abandon": "נטוש",
    "ability": "יכולת",
    ...
  },
  "native_to_english": {
    "נטוש": "abandon",
    "יכולת": "ability",
    ...
  }
}
```

Mappings are derived from index positions: word at index N in any language maps to word at index N in English. This is deterministic and verifiable against the raw wordlists.

**Use cases:**
- Build a multi-language BIP-39 wallet without generating your own mappings
- Display seed phrases in the user's native language
- Accept seed input in any supported language and resolve to English for standard BIP-39 derivation

## Design Principles

- **Strict BIP-39 compliance.** Every wordlist contains exactly 2048 words. No duplicates. No leading or trailing whitespace.
- **Deterministic structure.** Same file, same content, every time. Files are plain text, one word per line, UTF-8 encoded with Unix line endings.
- **Normalization awareness.** Non-Latin scripts require careful Unicode handling. See [`validation/encoding-notes.md`](validation/encoding-notes.md) for details on NFKD normalization and script-specific considerations.

## Wordlist Requirements

Each wordlist in this repository satisfies:

- Exactly 2048 words
- One word per line
- UTF-8 encoding
- No duplicate entries
- No leading or trailing whitespace
- Compatible with BIP-39 mnemonic generation and checksum derivation

## Usage

### Raw Wordlists

Load the appropriate file, split by newline, and index by position (0-2047). The word at index `i` corresponds to the 11-bit value `i` in BIP-39 entropy encoding.

```python
words = open("wordlists/official-bip39/english.txt").read().strip().split("\n")
assert len(words) == 2048
mnemonic_word = words[entropy_bits]
```

### Mappings

Load a mapping file and use it to translate between English and any supported language:

```python
import json

mapping = json.load(open("mappings/hebrew.json"))

# English to Hebrew (for display)
hebrew_word = mapping["english_to_native"]["abandon"]  # "נטוש"

# Hebrew to English (for restoration)
english_word = mapping["native_to_english"]["נטוש"]  # "abandon"
```

```javascript
const mapping = require('./mappings/hebrew.json');

// English to Hebrew
const hebrewWord = mapping.english_to_native['abandon']; // "נטוש"

// Hebrew to English
const englishWord = mapping.native_to_english['נטוש']; // "abandon"
```

## Security

- This repository does **not** implement a wallet.
- This repository does **not** generate seeds, derive keys, or sign transactions.
- These wordlists and mappings are reference data only.
- Use at your own risk. See [`DISCLAIMER.md`](DISCLAIMER.md).

## Validation

The `validation/` directory contains:

- `validate_all.py` — Automated validation script. Checks all 22 wordlists (2048 words, no duplicates, UTF-8, no BOM, no whitespace) and all 21 mappings (bidirectional consistency, entry count, round-trip integrity). Run with `python3 validation/validate_all.py`.
- `checksum-tests.json` — Valid and invalid mnemonic examples for testing.
- `encoding-notes.md` — UTF-8 and NFKD normalization guidance for non-Latin scripts, including ZWNJ handling for Farsi and NFKD impact summary per language.

## Why Farsi

April 1, 2026. Passover eve. Iran fires five ballistic missiles with splitting warheads at Tel Aviv. The founder of TZUR Wallet is in the shower when the alarm goes off. Between the sirens, an idea: if Iran is attacking Israel with missiles, Israel can answer with code. Code that helps the Iranian people. Not the regime. The people.

80+ million Iranians live under hyperinflation, banking restrictions, and capital controls. Their currency collapses. Their savings evaporate. They cannot move money freely. Bitcoin is their exit. But no Bitcoin wallet has ever spoken their language.

Until now.

The Farsi BIP-39 wordlist in this repository is the world's first. 2048 Persian words, each a meaningful translation of its English BIP-39 counterpart, designed so that an Iranian can recover their Bitcoin wallet in their mother tongue. The wordlist uses Farsi-specific characters (پ چ ژ گ) to ensure zero ambiguity with Arabic, and has zero word overlap with the Arabic wordlist.

An Israeli founder, under Iranian fire, building financial freedom tools for Iranian citizens. Not a marketing story. Just what happened.

**کلیدهای شما. زبان شما. بیت‌کوین شما.**
Your keys. Your language. Your Bitcoin.

**آزادی مالی.** Financial freedom.

---

## Contributing

Contributions are welcome, particularly:

- New language wordlists that follow the requirements above
- Corrections to existing wordlists (with justification)
- Additional test vectors

Please open an issue before submitting a PR for new languages.

## License

[MIT](LICENSE)

---

Maintained by the team behind [TZUR Wallet](https://github.com/osem23).
