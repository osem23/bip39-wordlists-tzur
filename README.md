# BIP-39 Wordlists

> Most Bitcoin wallets only support seed phrases in English. This repository provides BIP-39 compliant wordlists in 31 languages, including 15 languages (Arabic, Bengali, Danish, Estonian, Farsi, Filipino, Hebrew, Malay, Polish, Romanian, Swedish, Thai, Ukrainian, Urdu, Vietnamese) that had no known BIP-39 wordlists before this work. Built and maintained by the team behind [TZUR Wallet](https://tzur.live).

Strict, deterministic BIP-39 wordlists and bidirectional mappings for 31 languages.

Each wordlist contains exactly 2048 words, one per line, UTF-8 encoded. Each mapping provides a bidirectional English-to-native lookup, ready for use in any BIP-39 compliant wallet.

## Contents

### Wordlists

This repository contains three categories of wordlists:

#### TZUR Original Wordlists

These wordlists were created from scratch by the TZUR Wallet team. For 15 of them (Arabic, Bengali, Danish, Estonian, Farsi, Filipino, Hebrew, Malay, Polish, Romanian, Swedish, Thai, Ukrainian, Urdu, Vietnamese), no prior BIP-39 compliant wordlist existed before this work. For Dutch, German, Indonesian, Russian, and Turkish, prior BIP-39 lists exist from other projects; ours were created independently. Any vocabulary overlap with those reflects the natural frequency of common words in the language rather than derivation.

| Language | Wordlist | Mapping | Script |
|----------|----------|---------|--------|
| Arabic | [`wordlists/tzur-original/arabic.txt`](wordlists/tzur-original/arabic.txt) | [`mappings/arabic.json`](mappings/arabic.json) | Arabic |
| Bengali | [`wordlists/tzur-original/bengali.txt`](wordlists/tzur-original/bengali.txt) | [`mappings/bengali.json`](mappings/bengali.json) | Bengali (U+0980-U+09FF) |
| Danish | [`wordlists/tzur-original/danish.txt`](wordlists/tzur-original/danish.txt) | [`mappings/danish.json`](mappings/danish.json) | Latin (with æ ø å) |
| Dutch | [`wordlists/tzur-original/dutch.txt`](wordlists/tzur-original/dutch.txt) | [`mappings/dutch.json`](mappings/dutch.json) | Latin |
| Estonian | [`wordlists/tzur-original/estonian.txt`](wordlists/tzur-original/estonian.txt) | [`mappings/estonian.json`](mappings/estonian.json) | Latin (with ä ö ü õ) |
| Farsi (Persian) | [`wordlists/tzur-original/farsi.txt`](wordlists/tzur-original/farsi.txt) | [`mappings/farsi.json`](mappings/farsi.json) | Arabic (with پ چ ژ گ) |
| Filipino | [`wordlists/tzur-original/filipino.txt`](wordlists/tzur-original/filipino.txt) | [`mappings/filipino.json`](mappings/filipino.json) | Latin |
| German | [`wordlists/tzur-original/german.txt`](wordlists/tzur-original/german.txt) | [`mappings/german.json`](mappings/german.json) | Latin (with ä ö ü ß) |
| Hebrew | [`wordlists/tzur-original/hebrew.txt`](wordlists/tzur-original/hebrew.txt) | [`mappings/hebrew.json`](mappings/hebrew.json) | Hebrew |
| Indonesian | [`wordlists/tzur-original/indonesian.txt`](wordlists/tzur-original/indonesian.txt) | [`mappings/indonesian.json`](mappings/indonesian.json) | Latin |
| Malay | [`wordlists/tzur-original/malay.txt`](wordlists/tzur-original/malay.txt) | [`mappings/malay.json`](mappings/malay.json) | Latin |
| Polish | [`wordlists/tzur-original/polish.txt`](wordlists/tzur-original/polish.txt) | [`mappings/polish.json`](mappings/polish.json) | Latin (with ą ć ę ł ń ó ś ź ż) |
| Romanian | [`wordlists/tzur-original/romanian.txt`](wordlists/tzur-original/romanian.txt) | [`mappings/romanian.json`](mappings/romanian.json) | Latin (with ă â î ș ț, comma-below, not cedilla) |
| Russian | [`wordlists/tzur-original/russian.txt`](wordlists/tzur-original/russian.txt) | [`mappings/russian.json`](mappings/russian.json) | Cyrillic |
| Swedish | [`wordlists/tzur-original/swedish.txt`](wordlists/tzur-original/swedish.txt) | [`mappings/swedish.json`](mappings/swedish.json) | Latin (with å ä ö) |
| Thai | [`wordlists/tzur-original/thai.txt`](wordlists/tzur-original/thai.txt) | [`mappings/thai.json`](mappings/thai.json) | Thai |
| Turkish | [`wordlists/tzur-original/turkish.txt`](wordlists/tzur-original/turkish.txt) | [`mappings/turkish.json`](mappings/turkish.json) | Latin (with ç ğ ı ö ş ü) |
| Ukrainian | [`wordlists/tzur-original/ukrainian.txt`](wordlists/tzur-original/ukrainian.txt) | [`mappings/ukrainian.json`](mappings/ukrainian.json) | Cyrillic (with ї є і ґ) |
| Urdu | [`wordlists/tzur-original/urdu.txt`](wordlists/tzur-original/urdu.txt) | [`mappings/urdu.json`](mappings/urdu.json) | Perso-Arabic RTL (with ٹ ڈ ڑ ں ھ ے) |
| Vietnamese | [`wordlists/tzur-original/vietnamese.txt`](wordlists/tzur-original/vietnamese.txt) | [`mappings/vietnamese.json`](mappings/vietnamese.json) | Latin (with diacritics) |

#### Community Wordlists

Wordlists derived from existing community sources. Attribution is verified against the cited source.

| Language | Wordlist | Mapping | Notes |
|----------|----------|---------|-------|
| Hindi | [`wordlists/community/hindi.txt`](wordlists/community/hindi.txt) | [`mappings/hindi.json`](mappings/hindi.json) | Derived from [devnagri_wordlist](https://github.com/ujjwali2s/devnagri_wordlist) (98% match) |

#### Official BIP-39 Wordlists

Standard wordlists from the [BIP-39 specification](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki). Included here for completeness with mappings. These wordlists are not our work.

| Language | Wordlist | Mapping |
|----------|----------|---------|
| Chinese (Simplified) | [`wordlists/official-bip39/chinese_simplified.txt`](wordlists/official-bip39/chinese_simplified.txt) | [`mappings/chinese_simplified.json`](mappings/chinese_simplified.json) |
| Chinese (Traditional) | [`wordlists/official-bip39/chinese_traditional.txt`](wordlists/official-bip39/chinese_traditional.txt) | [`mappings/chinese_traditional.json`](mappings/chinese_traditional.json) |
| Czech | [`wordlists/official-bip39/czech.txt`](wordlists/official-bip39/czech.txt) | [`mappings/czech.json`](mappings/czech.json) |
| English | [`wordlists/official-bip39/english.txt`](wordlists/official-bip39/english.txt) | - (reference language) |
| French | [`wordlists/official-bip39/french.txt`](wordlists/official-bip39/french.txt) | [`mappings/french.json`](mappings/french.json) |
| Italian | [`wordlists/official-bip39/italian.txt`](wordlists/official-bip39/italian.txt) | [`mappings/italian.json`](mappings/italian.json) |
| Japanese | [`wordlists/official-bip39/japanese.txt`](wordlists/official-bip39/japanese.txt) | [`mappings/japanese.json`](mappings/japanese.json) |
| Korean | [`wordlists/official-bip39/korean.txt`](wordlists/official-bip39/korean.txt) | [`mappings/korean.json`](mappings/korean.json) |
| Portuguese | [`wordlists/official-bip39/portuguese.txt`](wordlists/official-bip39/portuguese.txt) | [`mappings/portuguese.json`](mappings/portuguese.json) |
| Spanish | [`wordlists/official-bip39/spanish.txt`](wordlists/official-bip39/spanish.txt) | [`mappings/spanish.json`](mappings/spanish.json) |

### Mappings

The `mappings/` directory contains bidirectional English-to-native JSON mapping files for all 30 non-English languages. Each mapping file includes:

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
- **4-char prefix uniqueness is not guaranteed.** BIP-39 suggests the first 4 characters of each word be unique (for typo-tolerant autocomplete). The official Trezor wordlists mostly meet this, with documented exceptions (Spanish accents, French phonetics). TZUR Original wordlists prioritize meaningful ordinal pairing with English over 4-char uniqueness. Implementations relying on 4-char autocomplete should fall back to full-word matching.

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

- `validate_all.py` - Automated validation script. Checks all 31 wordlists (2048 words, no duplicates, UTF-8, no BOM, no whitespace) and all 30 mappings (bidirectional consistency, entry count, round-trip integrity). Run with `python3 validation/validate_all.py`.
- `checksum-tests.json` - Valid and invalid mnemonic examples for testing.
- `encoding-notes.md` - UTF-8 and NFKD normalization guidance for non-Latin scripts, including ZWNJ handling for Farsi and NFKD impact summary per language.

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
