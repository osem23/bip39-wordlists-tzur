<pre>
  BIP: ?
  Layer: Applications
  Title: Native-language display wordlists for BIP-39 mnemonics
  Author: osem23 <ceo@blocksight.live>
  Comments-Summary: No comments yet.
  Comments-URI: https://github.com/bitcoin/bips/wiki/Comments:BIP-?
  Status: Draft
  Type: Informational
  Created: 2026-04-19
  License: BSD-2-Clause
</pre>

## Abstract

This document describes a convention for *native-language display wordlists* that accompany a BIP-39 English mnemonic. A display wordlist is a 2048-entry list in a target language, index-parallel to the canonical English BIP-39 wordlist, used by wallet software to render and accept the seed phrase in the user's native language without changing the mnemonic that is fed to PBKDF2.

The seed of record remains the canonical English BIP-39 mnemonic. A display wordlist is a UX layer; it adds no new cryptographic surface, and any seed produced under this convention remains restorable in any BIP-39 wallet using its English form.

## Motivation

A wallet that wants to show or accept the seed phrase in a language other than the eleven currently shipped with BIP-39 has two practical options: ship a parallel display wordlist that maps to English position-for-position, or ask the user to write down and later transcribe an English phrase in a language they may not read. The latter is error-prone at the point of backup. A single misspelling on paper, or a single mis-read during restore, fails the BIP-39 checksum and can render the seed unrecoverable. Many multilingual wallets already solve this internally by rendering the mnemonic in the user's native script. This document specifies the format and the integrity rules so that such display wordlists are interoperable across wallets and so that the cryptographic chain remains identical to a single-language BIP-39 implementation.

## Specification

### Definitions

- **Canonical mnemonic**: the English BIP-39 mnemonic produced by applying the BIP-39 specification to the wallet's entropy. It is the only mnemonic ever fed to PBKDF2-HMAC-SHA512 during seed derivation.
- **Display wordlist**: a 2048-entry list in a non-English language, index-parallel to the canonical English BIP-39 wordlist. The entry at index `i` is the native-language token corresponding to the English word at index `i`.
- **Display mnemonic**: the user-facing rendering of a canonical mnemonic using a display wordlist. Display mnemonics are never used as the password input to PBKDF2.

### Seed derivation

A wallet that uses a display wordlist derives the BIP-39 seed exclusively from the canonical English mnemonic:

1. Generate entropy as defined in BIP-39.
2. Compute the canonical English mnemonic per BIP-39.
3. Render the display mnemonic by replacing each English word at index `i` with the corresponding display wordlist entry at index `i`.
4. Show the display mnemonic to the user for backup.
5. On restore, accept the display mnemonic, look up each token in the display wordlist's reverse mapping to recover the canonical English mnemonic, then derive the seed per BIP-39.

The NFKD-normalized canonical English mnemonic from step 2 is the only input that ever reaches PBKDF2.

### Display wordlist requirements

A display wordlist MUST:

1. Contain exactly 2048 entries, one per line, UTF-8 encoded with no byte-order mark and Unix line endings (`\n`).
2. Have no duplicate entries.
3. Have no leading or trailing whitespace on any entry.
4. Have no embedded ASCII whitespace (`U+0020`) or ideographic space (`U+3000`) inside any entry. Mnemonic words are space-separated; an entry containing whitespace cannot survive the tokenization round trip required for paper-backup recovery.
5. Be paired with a bidirectional mapping (`english_to_native` and `native_to_english`) that is bijective across all 2048 entries.

A display wordlist SHOULD:

1. Maximize 4-character prefix uniqueness within the constraints of the target script. Realized uniqueness varies widely across scripts; wallets relying on prefix-based autocomplete fall back to full-word matching for any wordlist below 2048/2048 unique prefixes.
2. Be reviewed by a fluent native speaker before being shipped publicly.

Note on ordering: a display wordlist is stored in index-parallel order with the canonical English wordlist, not sorted by native-language collation. Those two orderings are mutually exclusive unless the English wordlist happens to be sorted by the target collation, which it is not. Lookup efficiency is provided by a hashmap over the 2048-entry native-to-English mapping; sorting by native collation is not a requirement of this convention.

### Input parsing

A wallet that accepts a display mnemonic on restore tokenizes it on whitespace before lookup:

1. Tokenize on Unicode whitespace (matching `.whitespacesAndNewlines` semantics) plus the ideographic space (`U+3000`) used by the official Japanese BIP-39 mnemonic.
2. Look up each token in the display wordlist's `native_to_english` mapping.
3. If any token is not present in the mapping, the input is invalid; the wallet does not silently substitute, partial-match, or fall through to a different wordlist.
4. After resolution, the resulting English token sequence is validated and used per BIP-39.

### Validation

Authors of a display wordlist verify the structural requirements above before publishing. A reference validator that enforces the MUST clauses is available at the reference registry below. It checks the 2048-word count, UTF-8 encoding without BOM, absence of duplicates, absence of leading or trailing whitespace, absence of embedded whitespace inside any entry, and round-trip consistency of the bidirectional mapping against the canonical English wordlist. SHOULD-clause metrics (4-character prefix uniqueness, native-speaker review status) are not enforced by the validator and are tracked separately in the registry's construction notes.

## Backwards Compatibility

Seeds produced under this convention are bit-identical to seeds produced by any BIP-39 implementation given the same entropy, because the canonical English mnemonic is the only PBKDF2 input in both cases. A user whose wallet supports a display wordlist can recover the seed in any BIP-39 wallet by entering the canonical English mnemonic.

## Reference Implementation

- Wordlist registry: <https://github.com/osem23/bip39-wordlists-tzur>. Contains 30 index-paired display wordlists with bidirectional mappings, plus the 10 canonical BIP-39 wordlists preserved at `wordlists/reference-canonical/` for spec comparison, plus a reference validator. Release tags track the display wordlist version; tag `v1.0.0` pins the initial 20-language set and `v1.1.0` adds the remaining 10 to reach 30.
- Construction notes: `docs/CONSTRUCTION.md` in the registry documents how each display wordlist was built, the disambiguation rules enforced, and the review status per language.
- Example decoders: `examples/python/`, `examples/javascript/`, and `examples/swift/` in the registry provide minimal reference implementations that convert a display mnemonic to its canonical English form and derive the BIP-39 seed. All three produce byte-identical seeds for the same input.
- Wallet implementation: <https://github.com/osem23/tzur-wallet>. The seed-derivation path resolves any display mnemonic to the canonical English mnemonic before computing PBKDF2; tests cover the paper-backup tokenization round trip per language.

## Test Vectors

The reference registry ships per-language conformance vectors under `test-vectors/`. Each file contains the canonical BIP-39 test entropy values (128, 160, 192, 224, and 256 bits) encoded as a mnemonic in the corresponding language, together with the derived seed. An implementation that reproduces every vector in a target language's file has a conformant encoding and PBKDF2 pipeline for that language.

The canonical English vector for 128-bit zero entropy with an empty passphrase is:

```
entropy  = 0x00000000000000000000000000000000
mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
seed     = 5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4
```

Per-language paper-backup round trips are exercised in the wallet implementation's test suite.

## Rationale

A display-only convention separates two concerns that are otherwise entangled. Cryptographic correctness stays with the canonical English BIP-39 wordlist, which is widely deployed and tested. Display and input vary per language without modifying anything that PBKDF2 sees. This keeps cross-wallet recoverability intact: every seed is restorable in any BIP-39 wallet via its English form, regardless of which display languages a given wallet supports.

The specific MUST clauses each address a concrete failure mode. Embedded whitespace inside an entry breaks the paper-backup round trip because mnemonic tokenization is whitespace-based; a multi-word entry fragments into two tokens that the wallet cannot resolve, and the seed becomes unrecoverable from text backup. Bijective mapping ensures that translation in either direction is unambiguous.

The 4-character prefix uniqueness recommendation from the original BIP-39 specification is achievable for English and most Latin-script languages but structurally infeasible for several scripts where word stems and limited short-prefix variety dominate. Requiring it would exclude those languages or force authorship of artificial vocabulary. Treating it as a SHOULD with informational reporting per language preserves the autocomplete benefit where feasible without excluding scripts where it is not.

Native-speaker review is recommended (SHOULD) rather than required (MUST) because its absence is a UX risk, not a cryptographic risk. The worst case is a poorly-chosen native word that a future PR can correct; no funds are at stake.

## Acknowledgments

This document builds on BIP-39 by Marek Palatinus, Pavol Rusnak, Aaron Voisine, and Sean Bowe.

## Copyright

This document is licensed under the BSD 2-clause license.
