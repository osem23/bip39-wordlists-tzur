# Compound Entries Audit

This document records the per-language audit of BIP-39 entries stored as glued multi-word compounds. A compound entry is one where the idiomatic native term for the English concept is a noun phrase, a spaced compound, or a particle construction in the target language, and is stored in this repository as a single orthographic token with no space, no hyphen, and no internal separator. The rationale and convention are described in [CONSTRUCTION.md § Multi-word concepts](CONSTRUCTION.md#multi-word-concepts).

The data file is [`validation/compound-entries.json`](../validation/compound-entries.json). The audit date is 2026-04-24.

## Purpose

Downstream wallets can use this dataset to show a small hint when a displayed seed phrase contains a compound entry, so the user does not insert whitespace when typing the seed back into another wallet. TZUR Wallet wires this into the seed-display and backup screens.

## Method

An entry is flagged as a compound by one of three mechanisms:

1. **Exact curated list.** Hebrew uses a manually reviewed list of 7 indices, built during the 2026-04-24 Hebrew compound audit. All other Hebrew entries were either replaced with single-word alternatives or confirmed as single words.
2. **Exact known set.** Romanian, French, Portuguese, Hindi, Ukrainian, and Estonian use the exact indices whose entries previously contained hyphens. Hyphens were normalized away to match the repository-wide no-separator convention; the set of pre-hyphenation compounds is definitionally the compound set (Romanian 76, French 6, Hindi 6, Ukrainian 2, Portuguese 1, Estonian 1 exact entries). Languages may include additional threshold-based entries beyond the exact set.
3. **Grapheme-length threshold.** For all other languages, entries whose grapheme-cluster length exceeds a language-calibrated threshold are flagged. Threshold values reflect each language's typical single-word length and morphology.

Thresholds used (grapheme clusters):

| Family | Threshold | Languages |
|---|---|---|
| RTL Semitic | 10 | ar, ur |
| Persian | 11 | fa |
| Indic | 11 | hi, bn |
| SE Asian | 11-12 | th, vi, id, ms |
| Philippine | 15 | fil |
| Turkic | 14 | tr |
| Germanic long-compound | 17-18 | de, nl |
| Slavic | 14-15 | ru, uk, pl, cs |
| Nordic | 15 | sv, da |
| Finno-Ugric | 15 | et |
| Romance | 15 | es, pt, fr, it |
| Other | curated | he, ro |
| Skipped | n/a | zh-Hans, zh-Hant, ja, ko |

Chinese, Japanese, and Korean are skipped. Their morphology is character-based, and the multi-word-compound concern that motivates this audit does not map onto them the same way.

Length-threshold detection admits false positives (long but single dictionary words flagged as compound) and false negatives (true compounds shorter than the threshold). The thresholds were tuned to keep each language's false-positive rate modest while catching the obvious cases. Hebrew and Romanian are exact and have neither false positives nor false negatives against the underlying curation.

## Per-language results

| Language | Locale | Compound count | 12-word seed trigger rate | Method |
|---|---|---:|---:|---|
| Romanian | ro | 76 | 36.5% | Exact (76 pre-dehyphenation indices) |
| Malay | ms | 24 | 13.2% | Threshold (>11 graphemes) |
| Farsi | fa | 23 | 12.7% | Threshold (>11 graphemes) |
| Indonesian | id | 13 | 7.4% | Threshold (>11 graphemes) |
| Vietnamese | vi | 12 | 6.8% | Threshold (>11 graphemes) |
| Hebrew | he | 7 | 4.0% | Curated |
| French | fr | 6 | 3.5% | Exact (6 pre-dehyphenation indices) |
| Hindi | hi | 6 | 3.5% | Exact (6 pre-dehyphenation indices) |
| Urdu | ur | 6 | 3.5% | Threshold (>10 graphemes) |
| Turkish | tr | 4 | 2.3% | Threshold (>14 graphemes) |
| Ukrainian | uk | 3 | 1.7% | Exact (2) + threshold (>15 graphemes) |
| Filipino | fil | 2 | 1.2% | Threshold (>15 graphemes) |
| Polish | pl | 2 | 1.2% | Threshold (>15 graphemes) |
| Estonian | et | 2 | 1.2% | Exact (1) + threshold (>15 graphemes) |
| Russian | ru | 1 | 0.6% | Threshold (>15 graphemes) |
| Portuguese | pt | 1 | 0.6% | Exact (1 pre-dehyphenation index) |
| Thai | th | 1 | 0.6% | Threshold (>12 graphemes) |
| Swedish | sv | 1 | 0.6% | Threshold (>15 graphemes) |
| Spanish | es | 0 | 0.0% | Threshold |
| German | de | 0 | 0.0% | Threshold |
| Italian | it | 0 | 0.0% | Threshold |
| Dutch | nl | 0 | 0.0% | Threshold |
| Arabic | ar | 0 | 0.0% | Threshold |
| Bengali | bn | 0 | 0.0% | Threshold |
| Czech | cs | 0 | 0.0% | Threshold |
| Danish | da | 0 | 0.0% | Threshold |
| Japanese | ja | — | — | Skipped (character-based) |
| Korean | ko | — | — | Skipped (character-based) |
| Chinese (Simplified) | zh-Hans | — | — | Skipped (character-based) |
| Chinese (Traditional) | zh-Hant | — | — | Skipped (character-based) |

Total flagged across all languages: **190 entries**.

The "trigger rate" column is the probability that a freshly generated 12-word BIP-39 mnemonic in that language contains at least one compound entry: `1 - ((2048 - count) / 2048) ** 12`.

## Data file

The exact index list per language is in [`validation/compound-entries.json`](../validation/compound-entries.json):

```json
{
  "audit_date": "2026-04-24",
  "audit_method": "...",
  "total_flagged": 190,
  "languages": {
    "hebrew": {"locale": "he", "count": 7, "indices": [468, 904, ...]},
    ...
  }
}
```

## Limitations and future work

- The threshold heuristic is coarse. A native-speaker review would reclassify some flagged entries as single words (false positives) and identify additional compounds below the threshold (false negatives). Native-speaker corrections land via issues and PRs against this file.
- Farsi uses ZWNJ (U+200C) as an orthographic compound-boundary marker. The current detection uses grapheme length only. A future pass could use ZWNJ presence as an additional signal.
- Chinese, Japanese, and Korean are skipped. If a downstream use case requires them, the detection method must be revisited for those scripts.
- The audit is static. When a wordlist is revised, this dataset must be regenerated.

## Regeneration

The data file is generated from the current `bip39-wordlists.json` source. Re-running the audit regenerates `validation/compound-entries.json` without regard to prior contents. It is not hand-edited.
