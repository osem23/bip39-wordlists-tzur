# Compound Entries

A compound entry is one where the idiomatic native term for the English concept is a noun phrase, a spaced compound, or a particle construction in the target language, stored here as a single orthographic token with no space, no hyphen, and no internal separator. The convention and rationale are in [`CONSTRUCTION.md § Multi-word concepts`](CONSTRUCTION.md#multi-word-concepts).

Data lives in [`validation/compound-entries.json`](../validation/compound-entries.json).

## Purpose

Downstream wallets use this dataset to show a small hint when a displayed seed phrase contains a compound entry, so the user does not insert whitespace when typing the seed back into another wallet. TZUR Wallet wires this into the seed-display and backup screens.

## Detection

A glued compound is a native entry that would normally carry a whitespace, hyphen, or Zero-Width Non-Joiner separator in everyday orthography, but is stored here as a single orthographic token to satisfy the repository's no-separator rule. Detection combines three independent signals. An entry is flagged when any signal confirms it; the set is a union, not an intersection.

### Signal 1 — translation dictionary

For every English BIP-39 word, Microsoft Azure Translator is queried for the native-language translation. When Azure's output contains an inline whitespace, hyphen, or Zero-Width Non-Joiner, the English concept maps to a multi-word native term in Azure's dictionary. Stripping those separators from Azure's output and comparing byte-for-byte against the stored entry (NFC-normalized, case-folded) confirms that the stored entry is the glued form of the same concept. This signal runs uniformly across all 30 languages and accounts for most of the flagged set. It is exact rather than heuristic: a flag fires only when the two forms are byte-identical modulo the stripped separator.

### Signal 2 — orthographic ground truth from the hyphen transition

Romanian, French, Hindi, Ukrainian, Estonian, and Portuguese formerly stored their compound entries with hyphens. The repository's structural rules forbid hyphens inside any entry; the hyphen-bearing set was therefore removed and replaced with glued forms. The set of entries that lost their hyphen is by construction the compound set for those languages. These indices are included even when Azure's dictionary happens to return a single-token synonym for the same concept.

### Signal 3 — native-speaker review for Hebrew

Hebrew received a full native-speaker review of its compound entries. Seven indices flagged during that review are carried in the dataset and merged with the Azure-filter output for Hebrew. Native review handles the residual cases where Azure's chosen synonym for an English concept is morphologically distinct from the stored compound and therefore does not match the filter byte-for-byte (for example, Azure renders "illegal" as `לא חוקי` while the stored entry is `בלתיחוקי`, a semantically equivalent but morphologically different compound).

### Scripts without word-level spacing

Japanese, Simplified Chinese, and Traditional Chinese do not delimit words with whitespace in their native orthography. The filter returns zero hits for those languages by construction; there is no separator for the filter to strip, so no compound concept in the sense defined above applies. Korean does delimit words with whitespace and is included in the dataset with five compounds.

### What the dataset does not claim

The flagged set is a lower bound, not a complete enumeration. A compound entry that Azure's dictionary does not translate with a separator, and that is not covered by the hyphen-transition set or by Hebrew's native review, is not captured by the current pipeline. Remaining gaps close through native-speaker contributions per language; corrections land via issue or pull request and are merged into the published dataset.

## Per-language counts

| Language | Locale | Count | % of wordlist | 12-word seed trigger rate |
|---|---|---:|---:|---:|
| Vietnamese | vi | 886 | 43.3% | 99.9% |
| Romanian | ro | 76 | 3.7% | 36.5% |
| Malay | ms | 57 | 2.8% | 28.7% |
| Urdu | ur | 45 | 2.2% | 23.4% |
| Indonesian | id | 29 | 1.4% | 15.7% |
| Farsi | fa | 22 | 1.1% | 12.2% |
| Turkish | tr | 20 | 1.0% | 11.1% |
| Hebrew | he | 17 | 0.8% | 9.5% |
| Filipino | fil | 10 | 0.5% | 5.7% |
| Hindi | hi | 9 | 0.4% | 5.1% |
| French | fr | 7 | 0.3% | 4.0% |
| Korean | ko | 5 | 0.2% | 2.9% |
| Ukrainian | uk | 4 | 0.2% | 2.3% |
| Danish | da | 4 | 0.2% | 2.3% |
| Portuguese | pt | 2 | 0.1% | 1.2% |
| Estonian | et | 2 | 0.1% | 1.2% |
| Bengali | bn | 2 | 0.1% | 1.2% |
| Arabic | ar | 1 | 0.0% | 0.6% |
| Thai | th | 1 | 0.0% | 0.6% |
| Dutch | nl | 1 | 0.0% | 0.6% |
| Spanish | es | 0 | 0.0% | 0.0% |
| German | de | 0 | 0.0% | 0.0% |
| Italian | it | 0 | 0.0% | 0.0% |
| Russian | ru | 0 | 0.0% | 0.0% |
| Polish | pl | 0 | 0.0% | 0.0% |
| Czech | cs | 0 | 0.0% | 0.0% |
| Swedish | sv | 0 | 0.0% | 0.0% |
| Japanese | ja | 0 | 0.0% | 0.0% |
| Chinese (Simplified) | zh-Hans | 0 | 0.0% | 0.0% |
| Chinese (Traditional) | zh-Hant | 0 | 0.0% | 0.0% |

Total flagged: **1200 entries**. **% of wordlist** is compound entries divided by 2048. **Trigger rate** is the probability that a freshly generated 12-word mnemonic contains at least one compound entry: `1 - ((2048 - count) / 2048) ** 12`.

**Vietnamese note.** Vietnamese natively separates syllables with spaces. Almost every multi-syllable Vietnamese entry in this repository is stored as one glued token while Azure's Vietnamese dictionary stores it with spaces. The count of 886 reflects the language's nature, not an error in the wordlist. Implementations should treat the "no extra spaces" hint as a near-certain signal for Vietnamese seeds.

## Dataset format

```json
{
  "total_flagged": 1200,
  "languages": {
    "hebrew": {"locale": "he", "count": 17, "indices": [44, 395, 468, ...]},
    "vietnamese": {"locale": "vi", "count": 886, "indices": [...]},
    "...": "..."
  }
}
```

Each language entry provides the iOS locale code, the number of flagged entries, and the index list. `total_flagged` is the sum across all languages.

The trigger rate for a 12-word BIP-39 seed in a given language is `1 - ((2048 - count) / 2048) ** 12`.

## Regeneration

The dataset is generated by applying the Azure forward-translation match against the current `bip39-wordlists.json` source and the exact hyphen sets. Regenerating replaces the file entirely; it is not hand-edited.
