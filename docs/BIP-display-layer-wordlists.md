<pre>
  BIP: ?
  Layer: Applications
  Title: Native-language display wordlists for BIP-39 mnemonics
  Author: Daniel Osemberg <ceo@blocksight.live>
  Discussions-To:
  Comments-Summary: No comments yet.
  Comments-URI: https://github.com/bitcoin/bips/wiki/Comments:BIP-?
  Status: Draft
  Type: Informational
  Created: 2026-04-19
  Post-History:
  License: BSD-2-Clause
</pre>

## Abstract

This document describes a convention for *native-language display wordlists* that accompany a BIP-39 English mnemonic. A display wordlist is a 2048-entry list in a target language, index-parallel to the canonical English BIP-39 wordlist, used by wallet software to render and accept the seed phrase in the user's native language without changing the mnemonic that is fed to PBKDF2.

The seed of record remains the canonical English BIP-39 mnemonic. A display wordlist is a UX layer; it adds no new cryptographic surface, and any seed produced under this convention remains restorable in any BIP-39 wallet using its English form.

## Motivation

A wallet that wants to show or accept the seed phrase in a language other than the ten currently shipped with BIP-39 (English plus nine non-English canonical wordlists) has two practical options: ship a parallel display wordlist that maps to English position-for-position, or ask the user to write down and later transcribe an English phrase in a language they may not read. The latter is error-prone at the point of backup. A single misspelling on paper, or a single mis-read during restore, fails the BIP-39 checksum and can render the seed unrecoverable. Many multilingual wallets already solve this internally by rendering the mnemonic in the user's native script. This document specifies the format and the integrity rules so that such display wordlists are interoperable across wallets and so that the cryptographic chain remains identical to a single-language BIP-39 implementation.

The 10 canonical BIP-39 wordlists cover roughly 35% of humanity by native language. The remaining 65%, around 5 billion native speakers, have no canonical wordlist in their language. A portable display-layer convention lets any wallet extend coverage without diverging from the BIP-39 cryptographic chain.

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
5. Be paired with a bidirectional mapping (`english_to_native` and `native_to_english`) that is bijective across all 2048 entries. This is the property that makes display-mnemonic to canonical-English-mnemonic resolution unambiguous in either direction.
6. Be stored in Unicode Normalization Form C (NFC). NFKD normalization is applied only to the canonical English mnemonic and the salt before PBKDF2, as BIP-39 already requires. The display wordlist itself never reaches PBKDF2.

A display wordlist SHOULD:

1. Maximize 4-character prefix uniqueness within the constraints of the target script. Realized uniqueness varies widely across scripts; wallets relying on prefix-based autocomplete fall back to full-word matching for any wordlist below 2048/2048 unique prefixes.
2. Be reviewed by a fluent native speaker of the target language before publication. Native-speaker review catches register, idiom, and cultural-neutrality issues that mechanical validation cannot.

Note on ordering: a display wordlist is stored in index-parallel order with the canonical English wordlist, not sorted by native-language collation. Those two orderings are mutually exclusive unless the English wordlist happens to be sorted by the target collation, which it is not. Lookup efficiency is provided by a hashmap over the 2048-entry native-to-English mapping; sorting by native collation is not a requirement of this convention.

### Input parsing

A wallet that accepts a display mnemonic on restore tokenizes it on whitespace before lookup:

1. Tokenize on Unicode whitespace (matching `.whitespacesAndNewlines` semantics) plus the ideographic space (`U+3000`) used by the official Japanese BIP-39 mnemonic.
2. Normalize every token and the display wordlist to the same Unicode form (NFC) before comparison. Mismatched normalization between input and wordlist causes silent lookup failures on precomposed/decomposed accent pairs.
3. Preserve Zero-Width Non-Joiner characters (`U+200C`) during tokenization of languages that use them (Persian/Farsi contains ZWNJ in a significant fraction of its entries). Strip ZWNJ for index lookup only when the wordlist's stored entries have been stripped; otherwise preserve ZWNJ in both directions. The choice MUST be consistent with how the wordlist was authored.
4. Look up each token in the display wordlist's `native_to_english` mapping.
5. If any token is not present in the mapping, the input is invalid; the wallet does not silently substitute, partial-match, or fall through to a different wordlist.
6. After resolution, the resulting English token sequence is validated and used per BIP-39.

### Validation

Authors of a display wordlist verify the structural requirements above before publishing. A reference validator at `validation/validate_all.py` in the reference registry enforces every MUST clause mechanically: exactly 2048 entries per file, UTF-8 encoding without BOM, absence of duplicates, absence of leading or trailing whitespace, absence of embedded whitespace inside any entry, NFC form, and round-trip consistency of the bidirectional mapping against the canonical English wordlist. SHOULD-clause metrics (4-character prefix uniqueness, native-speaker review status) are not enforced by the validator and are tracked separately in the registry's construction notes.

## Backwards Compatibility

Seeds produced under this convention are bit-identical to seeds produced by any BIP-39 implementation given the same entropy, because the canonical English mnemonic is the only PBKDF2 input in both cases. A user whose wallet supports a display wordlist can recover the seed in any BIP-39 wallet by entering the canonical English mnemonic.

## Reference Implementation

- **Wordlist registry.** <https://github.com/osem23/bip39-wordlists-tzur>, `main` branch. Ships 30 index-paired display wordlists with bidirectional mappings, the 10 canonical BIP-39 wordlists preserved at `wordlists/reference-canonical/` for spec comparison, and a reference validator at `validation/validate_all.py`. Tag `v1.0` pins an earlier snapshot for citation continuity.
- **Construction notes.** `docs/CONSTRUCTION.md` documents disambiguation rules, per-language notes, the three-layer translation-accuracy audit (structural validation, back-translation via Google Translate with LLM verdict, forward-translation via Microsoft Azure Translator with LLM verdict), and the review status matrix.
- **Canonical comparison.** `docs/canonical-vs-tzur.md` reports the word-set overlap between the 9 canonical non-English BIP-39 wordlists and their TZUR Original counterparts. The two are independent sources: Korean canonical and TZUR Original share zero tokens; Japanese shares 11; Latin-script languages share 400 to 700.
- **Example decoders.** `examples/python/decode.py`, `examples/javascript/decode.mjs`, and `examples/swift/Decode.swift`. Each resolves a display mnemonic to its canonical English form, applies NFKD, and derives the BIP-39 seed via PBKDF2. All three produce byte-identical seeds for the same input.
- **Wallet implementation.** <https://github.com/osem23/tzur-wallet>. The seed-derivation path resolves any display mnemonic to the canonical English mnemonic before computing PBKDF2; tests cover the paper-backup tokenization round trip per language.

## Test Vectors

The reference registry ships per-language conformance vectors under `test-vectors/`. Each file contains 14 vectors across the five canonical BIP-39 entropy lengths (128, 160, 192, 224, and 256 bits), each with a display-language mnemonic and the derived seed. Under this convention the display-language seed for a given entropy equals the English seed for the same entropy, by construction; this is the property that defines the convention. An implementation that reproduces every vector in a target language's file has a conformant encoding and PBKDF2 pipeline for that language.

The canonical English vector for 128-bit zero entropy with an empty passphrase is:

```
entropy  = 0x00000000000000000000000000000000
mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
seed     = 5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4
```

Per-language paper-backup round trips are exercised in the wallet implementation's test suite.

## Rationale

A display-only convention separates two concerns that are otherwise entangled. Cryptographic correctness stays with the canonical English BIP-39 wordlist, which has been deployed across the Bitcoin wallet ecosystem since 2013. Display and input vary per language without modifying anything that PBKDF2 sees. This keeps cross-wallet recoverability intact: every seed is restorable in any BIP-39 wallet via its English form, regardless of which display languages a given wallet supports.

The specific MUST clauses each address a concrete failure mode. Embedded whitespace inside an entry breaks the paper-backup round trip because mnemonic tokenization is whitespace-based; a multi-word entry fragments into two tokens that the wallet cannot resolve, and the seed becomes unrecoverable from text backup. The bijective mapping requirement ensures that translation in either direction is unambiguous. The NFC storage requirement prevents precomposed/decomposed accent mismatches from causing silent lookup failures on restore.

The 4-character prefix uniqueness recommendation from the original BIP-39 specification is achievable for English and most Latin-script languages but structurally infeasible for several scripts where word stems and limited short-prefix variety dominate. Requiring it would exclude those languages or force authorship of artificial vocabulary. Treating it as a SHOULD with informational reporting per language preserves the autocomplete benefit where feasible without excluding scripts where it is not.

Native-speaker review is recommended (SHOULD) rather than required (MUST) because its absence is a UX risk, not a cryptographic risk. The worst case is a poorly-chosen native word that a future PR can correct; no funds are at stake.

The 9 non-English canonical BIP-39 wordlists are alphabetized independent word selections, not translations of the English list, so they cannot serve as a display layer over an English mnemonic without the user facing semantically unrelated tokens at each index. This convention does not replace those wordlists; it sits parallel to them and fills the role they do not fill. The reference registry preserves the canonical wordlists at `wordlists/reference-canonical/` for anyone who needs to cite or compare against the spec, and ships the display-layer wordlists separately at `wordlists/tzur-original/`.

## Security Considerations

- **PBKDF2 input is invariant under this convention.** Only the canonical English mnemonic reaches PBKDF2-HMAC-SHA512. An implementation that feeds the display mnemonic directly to PBKDF2 is non-conformant and produces incompatible seeds. The conformance test vectors in the reference registry exercise the resolve-to-English path for every supported language.
- **Strict single-wordlist tokenization.** On restore, every token in the display mnemonic MUST resolve within a single display wordlist. Wallets MUST NOT silently accept mnemonics whose tokens span multiple wordlists, partial-match across wordlists, or fall through to the canonical English wordlist when a display token is unrecognized. Mixed-wordlist input is malformed and is rejected.
- **Only the canonical English mnemonic guarantees cross-wallet recovery.** A user whose wallet supports a display wordlist can always recover the seed in any BIP-39 wallet by entering the canonical English mnemonic. A user who backs up only the display mnemonic and then needs to restore in a wallet that does not support the same display wordlist cannot recover without the mapping. Wallets SHOULD make this property clear at backup time and SHOULD offer to display the canonical English mnemonic on demand.
- **Paper-backup corruption.** A single transcription error in the display mnemonic fails the BIP-39 checksum just as it would in English. The display layer does not introduce new recovery paths and does not relax the checksum requirement.
- **Wordlist integrity.** If an attacker substitutes the display wordlist stored on disk with a different list, the user's displayed mnemonic on restore will differ from what was backed up. Wallets SHOULD treat bundled wordlists as integrity-critical assets and verify them against a signed manifest at load time.
- **Native-speaker review is a UX risk, not a cryptographic risk.** Display wordlists without native-speaker review may contain culturally awkward, offensive, or regionally-inappropriate tokens. This affects user trust and backup legibility, not cryptographic correctness. Wordlist maintainers SHOULD publish native-speaker review status and accept corrections via pull request.

## Acknowledgments

This document builds on BIP-39 by Marek Palatinus, Pavol Rusnak, Aaron Voisine, and Sean Bowe.

## Copyright

This document is licensed under the BSD 2-clause license.
