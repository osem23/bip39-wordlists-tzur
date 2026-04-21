# Construction Notes

This document describes how the wordlists in this repository were constructed, the disambiguation rules applied, and the review status per language. It complements [`validation/encoding-notes.md`](../validation/encoding-notes.md), which covers Unicode and normalization, and the top-level [`README.md`](../README.md), which describes the repository layout.

## Table of contents

- [Scope and claims](#scope-and-claims)
- [Design principles](#design-principles)
- [Construction process](#construction-process)
- [Structural rules enforced on every wordlist](#structural-rules-enforced-on-every-wordlist)
- [Disambiguation and collision resolution](#disambiguation-and-collision-resolution)
- [Per-language construction notes](#per-language-construction-notes)
- [Review status matrix](#review-status-matrix)
- [Reproducibility](#reproducibility)
- [Known limitations](#known-limitations)

## Scope and claims

This repository contains:

- **30 TZUR Original display wordlists** (`wordlists/tzur-original/`). Built by [osem23](https://github.com/osem23), builder of TZUR Wallet. Each is an index-paired semantic translation of the canonical English BIP-39 wordlist. The construction process below describes these.
- **10 canonical BIP-39 wordlists** (`wordlists/reference-canonical/`). Sourced verbatim from the BIP-39 specification. Preserved here for spec comparison; not used by TZUR as a display layer, since the canonical non-English wordlists are alphabetized independent selections in their languages, not translations of English.

This document does not claim linguistic perfection. It describes what we did, how we did it, and which constraints we enforced.

## Design principles

The 30 TZUR Original wordlists follow four design principles:

1. **Index-paired translation.** For every index `N` in `0..2047`, the native word at line `N` is a direct semantic translation of `english.txt` line `N`. This property is what makes the bidirectional mapping deterministic: you do not need a lookup table to derive it; you just read both wordlists in parallel.

2. **English as the cryptographic floor.** A seed phrase in any native language is converted to its English equivalent (via the mapping) before PBKDF2 seed derivation. The native wordlist is a display and input layer, not a distinct cryptographic artifact. A Bengali seed phrase derives the same keys as the equivalent English phrase. Portability to any BIP-39 wallet is preserved through the mapping.

3. **Strict structural validity.** Every wordlist in this repository is checked by `validation/validate_all.py` for: exactly 2048 words, UTF-8 without BOM, no duplicates, no whitespace, Unix line endings, round-trip mapping integrity. No release tag is cut without this passing.

4. **Deterministic normalization.** Each wordlist is stored in NFC (canonical composition) precomposed form for readability. Cryptographic operations apply NFKD before PBKDF2 as required by BIP-39. Implementations that normalize inconsistently will produce different seeds; this is a correctness requirement of BIP-39 itself, not specific to this repository. See [`validation/encoding-notes.md`](../validation/encoding-notes.md).

## Construction process

Every TZUR Original wordlist passed through the same pipeline:

### Step 1. Baseline translation

For each index `N` in `0..2047`, the canonical English word at line `N` of `english.txt` was translated into the target language. The translation targets semantic equivalence of the single-word concept, not idiomatic phrasing. Compound or multi-word translations were rejected; every entry is a single orthographic word in the target language.

### Step 2. Length and character constraints

Each candidate native word must satisfy:

- Length between 2 and 16 characters (grapheme count, not byte count).
- No whitespace, no tab, no line break.
- NFC-normalized and valid UTF-8.
- Script-appropriate. Latin-alphabet languages do not accept Cyrillic entries and vice versa.

Candidates failing these checks were replaced with an alternative translation of the same English concept (e.g., a synonym, a close hyponym, or a morphologically simpler form).

### Step 3. Bijection enforcement

Duplicates are not permitted. If two different English words translated to the same native word, one of them was replaced with an alternative translation. Replacement always preferred keeping the most common English sense mapped to the most common native word, and moving the less-frequent English sense to a synonym or related form. This process is iterative: one round of replacements could introduce a new collision against a different index, so bijection was re-checked after every pass.

Collision counts on the first pass varied widely by language: Urdu had 144 first-pass collisions (highest), Danish had 9, Swedish had 4. Final bijection is clean across all 30 TZUR Original wordlists.

### Step 4. Structural validation

Each final wordlist was run through `validation/validate_all.py` and `mappings/<lang>.json` was regenerated by reading the wordlist in lockstep with `english.txt`. The mapping is derivable from the two files, not an independent artifact.

### Step 5. Translation-accuracy audit

Every TZUR Original wordlist passes structural validation and at least one translation-accuracy pass. Audit depth varies by language and is tracked in the review status matrix below.

**Layer 1. Structural validation.** `validation/validate_all.py` enforces exactly 2048 words, UTF-8 without BOM, no duplicates, no whitespace, Unix line endings, and bidirectional mapping round-trip integrity. Fully mechanical. Applied to all 30 TZUR Original wordlists.

**Layer 2. Back-translation pass (native to English).** Each native word is back-translated via Google Translate to English. Entries where the back-translation diverges from the original English at the same index are flagged as suspects. An LLM review agent evaluates each suspect by comparing the native word directly to the English (not trusting the back-translation blindly), and assigns CORRECT (loanword, morphological variant, or accepted synonym), CLOSE (plausible but imperfect), AMBIGUOUS (requires native-speaker input), or WRONG (incorrect). WRONG entries are replaced with a single-token alternative and the wordlist is re-validated. Applied to 29 of 30 TZUR Original wordlists; Czech is a follow-up pass.

**Layer 3. Forward-translation pass (English to native).** The same flow is run in the opposite direction using Microsoft Azure Translator. English is forward-translated to the target language; entries where Azure's rendering diverges from our native are flagged as suspects and reviewed by the same LLM verdict layer. This catches a different class of errors than layer 2, particularly false friends, homonym sense-shifts, and cases where the back-translation happens to agree with an incorrect native word. Applied to 19 of 30 TZUR Original wordlists (the 20 first-wave languages minus Hebrew, which was covered by native-speaker review on top of layers 1-3); the 10 second-wave languages have layer 3 as a scheduled follow-up.

Both translation engines are imperfect on their own. Back-translation is noisy on homographs and loanwords. Forward-translation has its own biases. The verdict layer treats both as filters that reduce the review set from 2048 to roughly 200 to 1,600 entries per language per pass, not as oracles. Final decisions are made by direct English-to-native comparison.

Aggregate audit figures at time of writing: 59,392 entries audited through at least one translation engine (29 languages × 2048). 821 entries flagged WRONG and replaced (1.38%): 228 across the 20 first-wave languages (three-layer audit) and 593 across 9 of the 10 second-wave languages (two-layer audit). Post-fix known error rate: 0% against the completed audit layers for each language. The refined wordlists are what this repository ships.

Back-translation and forward-translation are not substitutes for native-speaker review. Native speakers catch register, idiom, and cultural-neutrality issues that neither engine nor LLM layer reliably detects. Native-speaker contributions arrive via issues and PRs; acknowledgement is added to the review status matrix when each lands.

## Structural rules enforced on every wordlist

These rules are enforced mechanically by `validation/validate_all.py` and no release tag is cut without them passing:

| Rule | Enforcement |
|------|-------------|
| Exactly 2048 words | Line count of stripped file |
| UTF-8 encoded, no BOM | Byte inspection of first 3 bytes and decode test |
| No duplicate entries | `len(set(words)) == 2048` |
| No leading or trailing whitespace | Regex check per line |
| No embedded tab, CR, or LF within a word | Per-line character scan |
| Unix line endings | File read byte inspection |
| Mapping round-trip | `native_to_english[english_to_native[w]] == w` for every English word |
| Mapping completeness | Both directions have 2048 entries |

## Disambiguation and collision resolution

Several languages required specific disambiguation rules beyond the generic bijection enforcement.

- **Romanian.** Uses modern comma-below `ș/ț` (U+0219/U+021B), not legacy cedilla `ş/ţ` (U+015F/U+0163). Cedilla forms were converted to comma-below during construction. This matches the current Romanian Academy orthography.
- **Swedish and Danish.** Both scripts share `å` (U+00E5). The app-side language detection heuristic uses `ä/ö` (U+00E4/U+00F6) to disambiguate Swedish and `æ/ø` (U+00E6/U+00F8) to disambiguate Danish. Words containing only `å` without other disambiguating diacritics exist in both wordlists and are resolved at the application layer by dictionary membership. No wordlist word is identical across the two.
- **Urdu and Farsi.** Both use Perso-Arabic script. Urdu uses the distinct letters `ٹ ڈ ڑ ں ھ ے` (U+0679/0688/0691/06BA/06BE/06D2); Farsi uses `پ چ ژ گ`. Application-layer detection uses Urdu-specific letters first, then Farsi-specific, then Arabic as the fallback. Within each wordlist, no word crosses this boundary.
- **Farsi ZWNJ.** The Farsi wordlist contains 556 Zero-Width Non-Joiners across 534 words. This is linguistically correct Persian orthography for compound word boundaries. Implementations must handle ZWNJ consistently (strip for comparison, preserve for display). See [`validation/encoding-notes.md`](../validation/encoding-notes.md).
- **Chinese Simplified and Traditional.** Stored as independent wordlists. Some characters appear in both variants; they are not aliased.
- **Arabic, Hebrew, Urdu (RTL scripts).** Wordlists are stored in logical (memory) order, not visual order. Do not rely on editor display. Hebrew final-form letters (כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ) are distinct codepoints and are not conflated.
- **Vietnamese.** Uses precomposed NFC forms. 97.7% of entries are affected by NFKD decomposition. Implementations must apply NFKD before PBKDF2; failure to do so will produce different seeds.

## Per-language construction notes

| Language | Source | Canonical BIP-39? | Notes |
|---|---|---|---|
| Arabic | Translation | No prior known | RTL. 6.0% NFKD-affected. Hamza variations (أ إ ؤ ئ ء) treated as distinct codepoints. |
| Bengali | Translation | No prior known | Bengali script U+0980-U+09FF. Clean block, NFKD-stable. |
| Chinese (Simplified) | Translation | Canonical exists | Canonical spec list is a Han-character frequency ordering, not translation. TZUR Original is a semantic translation of English. |
| Chinese (Traditional) | Translation | Canonical exists | As above, traditional-character variant. |
| Czech | Translation | Canonical exists | Canonical spec list is an alphabetized independent Czech word set, not translation. TZUR Original is a semantic translation of English. Translation-accuracy audit is a scheduled follow-up. |
| Danish | Translation | No prior known | Latin with æ/ø/å. Disambiguated from Swedish via æ/ø. |
| Dutch | Translation | No canonical, prior lists exist from other projects | Ours was independently constructed. Overlap reflects common-word frequency, not derivation. |
| Estonian | Translation | No prior known | Latin with ä/ö/ü/õ. |
| Farsi | Translation | No prior known | Perso-Arabic RTL. 556 ZWNJ instances across 534 words is standard Persian orthography. |
| Filipino | Translation | No prior known | Latin. |
| French | Translation | Canonical exists | Canonical spec list is an alphabetized independent French word set, not translation. TZUR Original is a semantic translation of English. |
| German | Translation | No canonical, prior lists exist from other projects | Ours was independently constructed. |
| Hebrew | Translation | No prior known | RTL. Unpointed (no niqqud). Full native-speaker review by osem23. |
| Hindi | Translation | No canonical | No canonical Hindi exists in the BIP-39 spec. Prior community list (`devnagri_wordlist`) was superseded in this repository by a full TZUR Original translation. |
| Indonesian | Translation | No canonical, prior lists exist from other projects | Ours was independently constructed. |
| Italian | Translation | Canonical exists | Canonical spec list is an alphabetized independent Italian word set, not translation. TZUR Original is a semantic translation of English. |
| Japanese | Translation | Canonical exists | Canonical spec list is a hiragana ordering, not translation. TZUR Original uses kanji + kana and is a semantic translation of English. |
| Korean | Translation | Canonical exists | Canonical spec list is an alphabetized independent Korean word set, not translation. TZUR Original is a semantic translation of English. |
| Malay | Translation | No prior known | Latin. |
| Polish | Translation | No prior known | Latin with ą/ć/ę/ł/ń/ó/ś/ź/ż. |
| Portuguese | Translation | Canonical exists | Canonical spec list is an alphabetized independent Portuguese word set, not translation. TZUR Original is a semantic translation of English. |
| Romanian | Translation | No prior known | Comma-below ș/ț, not legacy cedilla. |
| Russian | Translation | No canonical, prior lists exist from other projects | Ours was independently constructed. 8.8% NFKD-affected. |
| Spanish | Translation | Canonical exists | Canonical spec list is an alphabetized independent Spanish word set, not translation. TZUR Original is a semantic translation of English. |
| Swedish | Translation | No prior known | Latin with å/ä/ö. Disambiguated from Danish via ä/ö. |
| Thai | Translation | No prior known | Thai script. 5.3% NFKD-affected. |
| Turkish | Translation | No canonical, prior lists exist from other projects | Ours was independently constructed. 29.1% NFKD-affected (highest among Latin TZUR Originals). |
| Ukrainian | Translation | No prior known | Cyrillic with ї/є/і/ґ. |
| Urdu | Translation | No prior known | Perso-Arabic RTL. 144 first-pass collisions (highest). |
| Vietnamese | Translation | No prior known | Latin with extensive diacritics. 97.7% NFKD-affected. |

"Canonical BIP-39?" records whether the BIP-39 specification ships a canonical wordlist for this language. Where a canonical exists, it is preserved at `wordlists/reference-canonical/` for spec comparison; see `docs/canonical-vs-tzur.md` for the per-index diff. "No prior known" reflects our research at time of publication. If a pre-existing wordlist surfaces for one of those languages, it will be acknowledged here and in the README.

## Review status matrix

The review status of each TZUR Original wordlist. Back-translation audit uses Google Translate. Forward-translation audit uses Microsoft Azure Translator. Both feed into the same LLM verdict layer. Refinements column counts the entries replaced after verdicts, summed across every completed audit layer for that language.

| Language | Structural | Back-translation | Forward-translation | Refinements | Native-speaker |
|---|---|---|---|---|---|
| Arabic | Clean | Complete | Complete | 4 | Pending |
| Bengali | Clean | Complete | Complete | 0 | Pending |
| Chinese (Simplified) | Clean | Complete | Pending | 85 | Pending |
| Chinese (Traditional) | Clean | Complete | Pending | 81 | Pending |
| Czech | Clean | Pending | Pending | — | Pending |
| Danish | Clean | Complete | Complete | 0 | Pending |
| Dutch | Clean | Complete | Complete | 1 | Pending |
| Estonian | Clean | Complete | Complete | 36 | Pending |
| Farsi | Clean | Complete | Complete | 0 | Pending |
| Filipino | Clean | Complete | Complete | 23 | Pending |
| French | Clean | Complete | Pending | 2 | Pending |
| German | Clean | Complete | Complete | 1 | Pending |
| Hebrew | Clean | Complete | Complete | 5 | Complete (osem23) |
| Hindi | Clean | Complete | Pending | 181 | Pending |
| Indonesian | Clean | Complete | Complete | 9 | Pending |
| Italian | Clean | Complete | Pending | 49 | Pending |
| Japanese | Clean | Complete | Pending | 42 | Pending |
| Korean | Clean | Complete | Pending | 43 | Pending |
| Malay | Clean | Complete | Complete | 3 | Pending |
| Polish | Clean | Complete | Complete | 4 | Pending |
| Portuguese | Clean | Complete | Pending | 2 | Pending |
| Romanian | Clean | Complete | Complete | 0 | Pending |
| Russian | Clean | Complete | Complete | 4 | Pending |
| Spanish | Clean | Complete | Pending | 108 | Pending |
| Swedish | Clean | Complete | Complete | 0 | Pending |
| Thai | Clean | Complete | Complete | 3 | Pending |
| Turkish | Clean | Complete | Complete | 24 | Pending |
| Ukrainian | Clean | Complete | Complete | 35 | Pending |
| Urdu | Clean | Complete | Complete | 63 | Pending |
| Vietnamese | Clean | Complete | Complete | 13 | Pending |

Total refinements across the 29 TZUR Original wordlists that have completed at least one translation-accuracy pass: 821 of 59,392 entries (1.38%). Post-fix known error rate against each language's completed audit layers: 0%. Czech is pending its first translation-accuracy pass and is not yet counted.

Native-speaker contributions are welcomed per language via issue or PR. Acknowledgements are added to this matrix as reviews land.

## Reproducibility

This repository does not claim literal regeneration from primary sources. A third party running the construction pipeline against the same English BIP-39 wordlist would not produce byte-identical outputs. Translation choice is not fully deterministic, and collision resolution admits multiple valid solutions.

What is reproducible and verifiable:

1. **Structural validity.** Any third party can run `validation/validate_all.py` and confirm that every wordlist satisfies the BIP-39 structural rules.
2. **Mapping round-trip.** Given a wordlist and `english.txt`, the mapping JSON can be regenerated line-by-line and must match the committed mapping byte-for-byte.
3. **Semantic fidelity of individual entries.** Any third party can independently translate `english.txt[N]` into the target language and compare. The back-translation audit is a systematic form of this check.
4. **Cryptographic determinism.** Given a mnemonic in any supported language, the seed derived via the mapping-to-English path and then PBKDF2 is identical across implementations. Test vectors in the companion `test-vectors/` directory demonstrate this.

Statement 4 is the only property that matters cryptographically. Statements 1 and 2 are mechanically checked. Statement 3 is audited.

## Known limitations

- **Translation quality varies by language.** Every wordlist is bijection-clean and structurally valid, but translation choice is a judgment call. Entries may be replaced by better alternatives as native-speaker reviews arrive.
- **No external cryptographic or linguistic audit has been performed.** Validation is mechanical. Independent review by external parties is welcome; acknowledgement happens when it lands.
- **Cross-wallet portability depends on integration.** The English wordlist is universally supported. A native-language seed phrase is portable to another wallet only if that wallet integrates the mapping from this repository.
- **The "first known" claim is best-effort.** See [`README.md`](../README.md).

Corrections land via issues and pull requests.
