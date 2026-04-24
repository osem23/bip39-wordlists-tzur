# Compound Entries

A compound entry is one where the idiomatic native term for the English concept is a noun phrase, a spaced compound, or a particle construction in the target language, stored here as a single orthographic token with no space, no hyphen, and no internal separator. The convention and rationale are in [`CONSTRUCTION.md § Multi-word concepts`](CONSTRUCTION.md#multi-word-concepts).

Data lives in [`validation/compound-entries.json`](../validation/compound-entries.json).

## Purpose

Downstream wallets use this dataset to show a small hint when a displayed seed phrase contains a compound entry, so the user does not insert whitespace when typing the seed back into another wallet. TZUR Wallet wires this into the seed-display and backup screens.

## Detection

An entry is flagged as a compound by:

1. **Curated list** for languages where a full native-speaker review of compound entries is available (Hebrew).
2. **Exact known set** for languages whose native orthography uses hyphens in compound entries. Since entries are stored without hyphens per repository convention, the set of hyphen-bearing entries is definitionally the compound set (Romanian, French, Hindi, Ukrainian, Estonian, Portuguese).
3. **Grapheme-length threshold** for other languages. Entries whose grapheme-cluster length exceeds a language-calibrated threshold are flagged. Thresholds reflect each language's typical single-word length and morphology.

Length-threshold detection admits false positives (long single dictionary words flagged as compound) and false negatives (short compounds below threshold). Curated and exact-set detection is precise within the compound category. Native-speaker corrections land via issue or pull request.

Chinese, Japanese, and Korean are not included: their morphology is character-based, and the multi-word-compound concern that motivates this dataset does not map onto them.

## Per-language counts

| Language | Locale | Compound count | 12-word seed trigger rate |
|---|---|---:|---:|
| Farsi | fa | 215 | 73.6% |
| Romanian | ro | 76 | 36.5% |
| Filipino | fil | 67 | 32.9% |
| Estonian | et | 39 | 20.6% |
| French | fr | 27 | 14.7% |
| Dutch | nl | 26 | 14.2% |
| Malay | ms | 24 | 13.2% |
| Danish | da | 22 | 12.2% |
| Indonesian | id | 13 | 7.4% |
| Vietnamese | vi | 12 | 6.8% |
| Hebrew | he | 7 | 4.0% |
| Hindi | hi | 6 | 3.5% |
| Urdu | ur | 6 | 3.5% |
| Czech | cs | 6 | 3.5% |
| Turkish | tr | 4 | 2.3% |
| Arabic | ar | 4 | 2.3% |
| Ukrainian | uk | 3 | 1.7% |
| Polish | pl | 2 | 1.2% |
| Russian | ru | 1 | 0.6% |
| Portuguese | pt | 1 | 0.6% |
| Thai | th | 1 | 0.6% |
| Bengali | bn | 1 | 0.6% |
| Swedish | sv | 1 | 0.6% |
| Spanish | es | 0 | 0.0% |
| German | de | 0 | 0.0% |
| Italian | it | 0 | 0.0% |
| Japanese | ja | — | — |
| Korean | ko | — | — |
| Chinese (Simplified) | zh-Hans | — | — |
| Chinese (Traditional) | zh-Hant | — | — |

Total flagged across all languages: **564 entries**.

## Thresholds

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

Hebrew and Romanian are curated and exact respectively; thresholds do not apply to them.

## Dataset format

```json
{
  "total_flagged": 190,
  "languages": {
    "hebrew": {"locale": "he", "count": 7, "indices": [468, 904, ...]},
    "romanian": {"locale": "ro", "count": 76, "indices": [...]},
    "...": "..."
  }
}
```

Each language entry provides the iOS locale code, the number of flagged entries, and the index list. `total_flagged` is the sum across all languages.

The trigger rate for a 12-word BIP-39 seed in a given language is `1 - ((2048 - count) / 2048) ** 12`.

## Regeneration

The dataset is generated from the current `bip39-wordlists.json` source. Regenerating replaces the file entirely; it is not hand-edited.
