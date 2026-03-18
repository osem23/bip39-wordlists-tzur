# BIP-39 Wordlists

Strict, deterministic BIP-39 wordlists for 21 languages.

Each file contains exactly 2048 words, one per line, UTF-8 encoded. Suitable for use in any BIP-39 compliant wallet implementation.

## Contents

This repository contains three categories of wordlists:

### Original Wordlists

These wordlists were created from scratch by the TZUR Wallet team. To our knowledge, no prior BIP-39 compliant wordlists existed for these languages before this work.

| Language | File | Script |
|----------|------|--------|
| Arabic | [`wordlists/tzur-original/arabic.txt`](wordlists/tzur-original/arabic.txt) | Arabic |
| Filipino | [`wordlists/tzur-original/filipino.txt`](wordlists/tzur-original/filipino.txt) | Latin |
| Hebrew | [`wordlists/tzur-original/hebrew.txt`](wordlists/tzur-original/hebrew.txt) | Hebrew |
| Malay | [`wordlists/tzur-original/malay.txt`](wordlists/tzur-original/malay.txt) | Latin |
| Thai | [`wordlists/tzur-original/thai.txt`](wordlists/tzur-original/thai.txt) | Thai |
| Vietnamese | [`wordlists/tzur-original/vietnamese.txt`](wordlists/tzur-original/vietnamese.txt) | Latin (with diacritics) |

### Community Wordlists

Wordlists assembled during development, sourced or adapted from community contributions. Attribution is noted where applicable.

| Language | File | Notes |
|----------|------|-------|
| Dutch | [`wordlists/community/dutch.txt`](wordlists/community/dutch.txt) | Based on [OpenTaal BIP-39](https://github.com/OpenTaal/opentaal-bip39) |
| German | [`wordlists/community/german.txt`](wordlists/community/german.txt) | |
| Hindi | [`wordlists/community/hindi.txt`](wordlists/community/hindi.txt) | Based on [devnagri_wordlist](https://github.com/ujjwali2s/devnagri_wordlist) |
| Indonesian | [`wordlists/community/indonesian.txt`](wordlists/community/indonesian.txt) | Based on [perl-WordList-ID-BIP39](https://github.com/perlancar/perl-WordList-ID-BIP39) |
| Russian | [`wordlists/community/russian.txt`](wordlists/community/russian.txt) | |
| Turkish | [`wordlists/community/turkish.txt`](wordlists/community/turkish.txt) | |

### Official BIP-39 Wordlists

Standard wordlists from the [BIP-39 specification](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki). Included here for completeness. These are not our work.

| Language | File |
|----------|------|
| Chinese (Simplified) | [`wordlists/official-bip39/chinese_simplified.txt`](wordlists/official-bip39/chinese_simplified.txt) |
| Chinese (Traditional) | [`wordlists/official-bip39/chinese_traditional.txt`](wordlists/official-bip39/chinese_traditional.txt) |
| English | [`wordlists/official-bip39/english.txt`](wordlists/official-bip39/english.txt) |
| French | [`wordlists/official-bip39/french.txt`](wordlists/official-bip39/french.txt) |
| Italian | [`wordlists/official-bip39/italian.txt`](wordlists/official-bip39/italian.txt) |
| Japanese | [`wordlists/official-bip39/japanese.txt`](wordlists/official-bip39/japanese.txt) |
| Korean | [`wordlists/official-bip39/korean.txt`](wordlists/official-bip39/korean.txt) |
| Portuguese | [`wordlists/official-bip39/portuguese.txt`](wordlists/official-bip39/portuguese.txt) |
| Spanish | [`wordlists/official-bip39/spanish.txt`](wordlists/official-bip39/spanish.txt) |

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

These are raw wordlists. Load the appropriate file, split by newline, and index by position (0-2047). The word at index `i` corresponds to the 11-bit value `i` in BIP-39 entropy encoding.

```
words = read("wordlists/official-bip39/english.txt").split("\n")
assert len(words) == 2048
mnemonic_word = words[entropy_bits]
```

## Security

- This repository does **not** implement a wallet.
- This repository does **not** generate seeds, derive keys, or sign transactions.
- These wordlists are reference data only.
- Use at your own risk. See [`DISCLAIMER.md`](DISCLAIMER.md).

## Validation

The `validation/` directory contains:

- `checksum-tests.json` — Valid and invalid mnemonic examples for testing
- `encoding-notes.md` — UTF-8 and NFKD normalization guidance for non-Latin scripts

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
