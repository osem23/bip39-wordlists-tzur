# Construction Notes

This document describes how the wordlists in this repository are constructed, the rules they follow, and per-language characteristics. It complements [`validation/encoding-notes.md`](../validation/encoding-notes.md) on Unicode and normalization, and the top-level [`README.md`](../README.md) on repository layout.

## Table of contents

- [Scope and claims](#scope-and-claims)
- [Design principles](#design-principles)
- [Structural rules](#structural-rules)
- [Disambiguation rules](#disambiguation-rules)
- [Multi-word concepts](#multi-word-concepts)
- [Per-language notes](#per-language-notes)
- [Validation](#validation)
- [Reproducibility](#reproducibility)
- [Known limitations](#known-limitations)

## Scope and claims

This repository contains:

- **30 TZUR Original display wordlists** (`wordlists/tzur-original/`). Built by [osem23](https://github.com/osem23), builder of TZUR Wallet. Each is an index-paired semantic translation of the canonical English BIP-39 wordlist.
- **10 canonical BIP-39 wordlists** (`wordlists/reference-canonical/`). Sourced verbatim from the BIP-39 specification. Preserved here for spec comparison; not used as a display layer, since the canonical non-English wordlists are alphabetized independent selections in their languages, not translations of English.

This document describes what the wordlists are and the constraints they satisfy.

## Design principles

The 30 TZUR Original wordlists follow four design principles.

1. **Index-paired translation.** For every index `N` in `0..2047`, the native word at line `N` is a direct semantic translation of `english.txt` line `N`. The bidirectional mapping is derivable; it does not require a lookup table.

2. **English as the cryptographic floor.** A seed phrase in any native language is converted to its English equivalent through the mapping before PBKDF2 derivation. The native wordlist is a display and input layer, not a distinct cryptographic artifact. A Bengali seed phrase derives identical keys to the equivalent English phrase.

3. **Strict structural validity.** Every wordlist is checked by `validation/validate_all.py` for exactly 2048 words, UTF-8 without BOM, no duplicates, no whitespace, Unix line endings, and round-trip mapping integrity.

4. **Deterministic normalization.** Wordlists are stored in NFC precomposed form. Cryptographic operations apply NFKD before PBKDF2 as required by BIP-39. See [`validation/encoding-notes.md`](../validation/encoding-notes.md).

## Structural rules

Rules enforced mechanically by `validation/validate_all.py`:

| Rule | Enforcement |
|------|-------------|
| Exactly 2048 words | Line count of stripped file |
| UTF-8 encoded, no BOM | Byte inspection and decode test |
| No duplicate entries | `len(set(words)) == 2048` |
| No leading or trailing whitespace | Per-line regex check |
| No embedded tab, CR, or LF within a word | Per-line character scan |
| No hyphen or space within a word | Per-line character scan |
| Unix line endings | Byte inspection |
| Mapping round-trip | `native_to_english[english_to_native[w]] == w` for every English word |
| Mapping completeness | Both directions have 2048 entries |

## Disambiguation rules

- **Romanian.** Uses modern comma-below `ș/ț` (U+0219/U+021B), not legacy cedilla `ş/ţ` (U+015F/U+0163).
- **Swedish and Danish.** Both scripts share `å` (U+00E5). Application-layer language detection uses `ä/ö` (U+00E4/U+00F6) to disambiguate Swedish and `æ/ø` (U+00E6/U+00F8) to disambiguate Danish. No wordlist word is identical across the two.
- **Urdu and Farsi.** Both use Perso-Arabic script. Urdu-distinct letters `ٹ ڈ ڑ ں ھ ے` (U+0679/0688/0691/06BA/06BE/06D2) disambiguate Urdu; Farsi-distinct letters `پ چ ژ گ` disambiguate Farsi.
- **Farsi ZWNJ.** The Farsi wordlist contains 556 Zero-Width Non-Joiners across 534 words; this is standard Persian orthography for compound-word boundaries. Implementations strip for comparison and preserve for display.
- **Chinese Simplified and Traditional.** Stored as independent wordlists. Some characters appear in both variants; they are not aliased.
- **Arabic, Hebrew, Urdu (RTL scripts).** Stored in logical (memory) order. Hebrew final-form letters (כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ) are distinct codepoints and not conflated.
- **Vietnamese.** Precomposed NFC forms. 97.7% of entries are affected by NFKD decomposition. Implementations apply NFKD before PBKDF2; failure to do so produces different seeds.

## Multi-word concepts

A subset of BIP-39 English entries names a concept that several target languages express only as a multi-word term: a noun phrase, a spaced compound, or a particle construction. "Dentist", "walnut", "coconut", "zoo", "wrist", "weather", "illegal" are common examples.

Where a language has no single-word equivalent, the idiomatic multi-word term is stored as one orthographic token with no space, no hyphen, no internal separator. Hebrew `רופא שיניים` (dentist) is stored as `רופאשיניים`. Turkish `hindistan cevizi` (coconut) is stored as `hindistancevizi`. Indonesian `kebun binatang` (zoo) is stored as `kebunbinatang`. Romanian `broască țestoasă` (turtle) is stored as `broascățestoasă`.

The convention is uniform across every wordlist in this repository: no space, no hyphen, no separator. The rationale is BIP-39 itself: encoding splits a mnemonic on whitespace, so any multi-word token would be parsed as two entries and break derivation. A glued token is the only form that round-trips through any BIP-39 implementation.

Per-language compound entry counts and exact index lists are in [`docs/compound-entries.md`](compound-entries.md) and [`validation/compound-entries.json`](../validation/compound-entries.json). Downstream wallets use this dataset to hint users against inserting whitespace when re-typing a seed containing a compound entry in another wallet.

## Per-language notes

| Language | Script | Canonical BIP-39? |
|---|---|---|
| Arabic | Arabic RTL (6.0% NFKD-affected) | No prior known |
| Bengali | Bengali (U+0980-U+09FF) | No prior known |
| Chinese (Simplified) | Han (Simplified) | Canonical exists |
| Chinese (Traditional) | Han (Traditional) | Canonical exists |
| Czech | Latin with diacritics | Canonical exists |
| Danish | Latin with æ/ø/å | No prior known |
| Dutch | Latin | Independent prior lists |
| Estonian | Latin with ä/ö/ü/õ | No prior known |
| Farsi | Perso-Arabic RTL (ZWNJ) | No prior known |
| Filipino | Latin | No prior known |
| French | Latin | Canonical exists |
| German | Latin with ä/ö/ü/ß | Independent prior lists |
| Hebrew | Hebrew RTL, unpointed | No prior known |
| Hindi | Devanagari | No canonical |
| Indonesian | Latin | Independent prior lists |
| Italian | Latin | Canonical exists |
| Japanese | Kanji + Kana | Canonical exists |
| Korean | Hangul | Canonical exists |
| Malay | Latin | No prior known |
| Polish | Latin with ą/ć/ę/ł/ń/ó/ś/ź/ż | No prior known |
| Portuguese | Latin | Canonical exists |
| Romanian | Latin with comma-below ș/ț | No prior known |
| Russian | Cyrillic (8.8% NFKD-affected) | Independent prior lists |
| Spanish | Latin | Canonical exists |
| Swedish | Latin with å/ä/ö | No prior known |
| Thai | Thai (5.3% NFKD-affected) | No prior known |
| Turkish | Latin (29.1% NFKD-affected) | Independent prior lists |
| Ukrainian | Cyrillic with ї/є/і/ґ | No prior known |
| Urdu | Perso-Arabic RTL | No prior known |
| Vietnamese | Latin with extensive diacritics (97.7% NFKD-affected) | No prior known |

"Canonical BIP-39?" records whether the BIP-39 specification ships a canonical wordlist for this language. Where a canonical exists, it is preserved at `wordlists/reference-canonical/` for spec comparison; see `docs/canonical-vs-tzur.md` for the per-index diff. "No prior known" reflects research at time of publication. If a pre-existing wordlist surfaces for one of those languages, it will be acknowledged here and in the README.

## Validation

Every wordlist passes three validation layers before release.

1. **Structural.** `validation/validate_all.py` enforces the rules above. Fully mechanical.
2. **Back-translation.** Native-to-English translation via Google Translate, with LLM verdict review comparing native directly to English at each index.
3. **Forward-translation.** English-to-native translation via Microsoft Azure Translator, with the same verdict layer. Catches false friends and homonym sense-shifts that back-translation alone misses.

Hebrew, Spanish, and Portuguese also carry native-speaker review. The remaining languages carry the three validation layers and are open to native-speaker corrections via issue or pull request.

### Translation re-run scope (2026-04-19)

The translation-validation pipeline was run twice. The initial run covered all 30 TZUR Original wordlists. A second run on 2026-04-19 covered ten languages: Bengali, Danish, Estonian, Farsi, Hebrew, Polish, Romanian, Swedish, Ukrainian, Urdu. The re-run scope was deliberately narrow and worth documenting, because a reader of `validation/translation-validation-report.md` will otherwise wonder why some languages have rerun-source rows and others do not.

Re-run inclusion criterion: a language was re-run if and only if its wordlist had been edited between the initial run and 2026-04-19 in response to the initial run's findings. The re-run measures the post-correction wordlist against the same translation-engine pipeline and confirms that the corrections moved the WRONG counts down.

Re-run exclusion criterion: a language was not re-run if its wordlist had not changed between the initial run and 2026-04-19. Re-running an unchanged wordlist would only test the stability of Google Translate plus the LLM verdict layer over time, not the wordlist itself, and would not produce useful evidence for or against the wordlist's quality.

Czech specifically. The initial run flagged 615 of 764 suspects as `WRONG` on Czech back-translation. That is the loudest data point in the report. Czech was not re-run on 2026-04-19, because its corrections were applied through a different process before the rerun window: the Czech wordlist underwent a structured construction-and-correction cycle documented in the §Per-language notes section of this document, with entry-level review against the English BIP-39 list rather than a second pipeline pass. The currently-published Czech wordlist reflects the post-correction state. The 615 number in the translation report is the pre-correction reading and will not reproduce against the current artifact. Re-running Czech against the current wordlist requires a fresh API run and would be its own session.

Filipino, Vietnamese, and the other initial-only rows whose `Back WRONG` count is below the 100-entry threshold were left at their initial readings because the corrections moved the count low enough that a re-run was not load-bearing for the report's headline accuracy claim. The initial-run numbers stand as the recorded result.

The general principle: the translation report describes wordlist state, not pipeline runs. Where the wordlist has moved since the recorded run, the report's per-row state notes call that out explicitly.

## Reproducibility

This repository does not claim literal regeneration from primary sources. A third party running the construction pipeline against the same English BIP-39 wordlist would not produce byte-identical outputs; translation choice is not fully deterministic.

What is reproducible and verifiable:

1. **Structural validity.** Run `validation/validate_all.py` to confirm every wordlist satisfies the BIP-39 structural rules.
2. **Mapping round-trip.** Given a wordlist and `english.txt`, the mapping JSON is regenerable line-by-line and must match the committed mapping byte-for-byte.
3. **Semantic fidelity of individual entries.** Any third party can independently translate `english.txt[N]` into the target language and compare.
4. **Cryptographic determinism.** Given a mnemonic in any supported language, the seed derived via the mapping-to-English path and then PBKDF2 is identical across implementations. Test vectors in `test-vectors/` demonstrate this.

Cryptographic determinism is the only property that matters cryptographically. Structural validity and round-trip are mechanical. Semantic fidelity is auditable.

## Known limitations

- Native-speaker review is complete for Hebrew, peer-reviewed for Spanish and Portuguese, and open for other languages.
- No external cryptographic or linguistic audit has been performed. Independent review is welcome.
- Cross-wallet portability depends on integration. The English wordlist is universally supported. A native-language seed phrase is portable to another wallet only if that wallet integrates the mapping from this repository.
- "No prior known" claims are best-effort at time of publication.

Corrections land via issues and pull requests.
