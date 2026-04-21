# Canonical BIP-39 vs TZUR Original

This document compares each of the 9 non-English canonical BIP-39 wordlists (spec-defined) with its TZUR Original counterpart.

**Two different objects stored under the same filename in two directories.** The canonical entry (under `wordlists/reference-canonical/`) is an independently-authored, alphabetized word in the target language, selected by the BIP-39 spec for uniqueness of 4-character prefix and native-script ordering. The TZUR Original entry (under `wordlists/tzur-original/`) is a semantic translation of the English BIP-39 word at the same index. Both are valid BIP-39 wordlists structurally and both contain exactly 2048 entries; what differs is which native words are in the list.

**Index ordering.** The TZUR Original is aligned to English position-for-position, so the mapping `english_to_native[english.txt[N]] = tzur_original[N]` is derivable mechanically. The canonical BIP-39 non-English lists are not — they are sorted by native-script collation, so the canonical word at index N has no semantic tie to the English word at index N.

**Cryptographic floor unchanged.** PBKDF2 runs on the English form. A seed in any TZUR Original display wordlist derives bit-identical keys to its English equivalent. Interoperability with any BIP-39 wallet is preserved through the mapping.

## Word-set difference

How many distinct tokens the two files share at all, regardless of where each appears. Both files always hold exactly 2048 entries; the interesting figure is how much the token sets overlap and how much is unique to each side.

| Language | Shared (in both) | Only in canonical | Only in TZUR |
|---|---:|---:|---:|
| Spanish | 705 | 1343 | 1343 |
| French | 495 | 1553 | 1553 |
| Italian | 430 | 1618 | 1618 |
| Portuguese | 423 | 1625 | 1625 |
| Czech | 303 | 1745 | 1745 |
| Japanese | 11 | 2037 | 2037 |
| Korean | 0 | 2048 | 2048 |
| Chinese (Simplified) | 75 | 1973 | 1973 |
| Chinese (Traditional) | 45 | 2003 | 2003 |
| **Combined** | **2487** | **15945** | **15945** |

Reading the figures:

- **Korean: 0 shared.** The canonical spec list is alphabetized Korean common words. The TZUR Original is a semantic translation of the English BIP-39 vocabulary. The two sets are disjoint — every one of the 2048 tokens appears in exactly one list.
- **Japanese: 11 shared.** Same reason as Korean, but hiragana-only canonical versus kanji + kana TZUR Original leaves minimal incidental overlap.
- **Chinese (Simplified 75, Traditional 45).** The canonical lists are single-character frequency-ordered dictionaries, while the TZUR Original is multi-character semantic translation. Overlap is the set of simple words (e.g., translation, language, action) that appear in both spaces.
- **Latin-script languages (Spanish, French, Italian, Portuguese).** 400-700 shared tokens reflects common-word overlap: the canonical list samples frequent single-morpheme native words, and the TZUR Original often lands on the same common native word when translating a common English concept.
- **Czech: 303 shared.** In line with the other Latin-script languages after the back-translate + LLM-verdict audit replaced the initial canonical-fallback placeholders with proper translations. Before the audit this figure was 844; the drop is the audit's effect.

The "Only in canonical" / "Only in TZUR" columns are symmetric per row because both lists hold exactly 2048 entries: whatever one list contributes that the other does not, the other must contribute in equal measure on its side.
