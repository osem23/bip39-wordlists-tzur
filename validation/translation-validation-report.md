# Translation Validation Report

Per-language results from the back-translation and forward-translation validation passes for the 30 TZUR Original wordlists. Wordlist size is 2048 entries per language.

## Methodology

Two automated translation passes are run over each wordlist, both with an LLM verdict layer.

- **Back-translation.** Native to English, via Google Translate. The LLM compares each native entry directly against the canonical English BIP-39 entry at the same index. Entries with cosine similarity below a 0.65 threshold are flagged as `suspect_count` and routed through the LLM, which assigns one of `CORRECT`, `CLOSE`, `WRONG`, or `OTHER`. Entries at or above the threshold are presumed correct without LLM review.
- **Forward-translation.** English to native, via Microsoft Azure Translator. Same suspect-and-verdict pipeline. Catches false friends and homonym sense-shifts that back-translation can miss when the native word back-translates cleanly to a synonym of the original English.

**Reading the suspect counts.** Suspect counts vary widely by language and are not in themselves an accuracy signal. Languages that are script-distant from English (Arabic, Hindi, Korean, Bengali, Thai, Vietnamese) commonly have hundreds or thousands of entries flagged as suspect because cosine similarity between non-Latin tokens and their English BIP-39 counterparts is low by construction. The accuracy signal is the post-review `WRONG` count, not the raw suspect count. A language with 1500 suspects and 3 WRONG is in better shape than a language with 200 suspects and 30 WRONG.

Ten languages were re-run on 2026-04-19 after corrections from the initial pass (Bengali, Danish, Estonian, Farsi, Hebrew, Polish, Romanian, Swedish, Ukrainian, Urdu). The report uses the rerun for back-translation in those languages and the initial run elsewhere; the `source_run` field in the JSON records which run each row comes from. Re-run scope rationale is documented in [`docs/CONSTRUCTION.md`](../docs/CONSTRUCTION.md).

`WRONG` is the count that matters for accuracy: it is the number of suspect entries the LLM judged as a wrong translation after review. The `WRONG` column in the table below is the back-translation count followed by the forward-translation count.

## Results

| Language | Back suspects | Back WRONG | Back source | Forward suspects | Forward WRONG | Forward source |
|---|---:|---:|---|---:|---:|---|
| arabic | 550 | 1 | initial | 1636 | 3 | initial |
| bengali | 525 | 46 | rerun_20260419 | 1035 | 5 | initial |
| chinese_simplified | 248 | 85 | initial | 996 | 1 | initial |
| chinese_traditional | 249 | 81 | initial | 1491 | 1 | initial |
| czech | 764 | 615 | initial | 972 | 10 | initial |
| danish | 207 | 0 | rerun_20260419 | 885 | 0 | initial |
| dutch | 262 | 0 | initial | 834 | 1 | initial |
| estonian | 408 | 28 | rerun_20260419 | 948 | 66 | initial |
| farsi | 504 | 0 | rerun_20260419 | 1188 | 79 | initial |
| filipino | 497 | 20 | initial | 1136 | 3 | initial |
| french | 230 | 1 | initial | 772 | 0 | initial |
| german | 250 | 0 | initial | 820 | 1 | initial |
| hebrew | 369 | 8 | rerun_20260419 | 881 | 4 | initial |
| hindi | 400 | 25 | initial | 1280 | 0 | initial |
| indonesian | 408 | 6 | initial | 964 | 3 | initial |
| italian | 258 | 0 | initial | 816 | 0 | initial |
| japanese | 246 | 42 | initial | 1195 | 2 | initial |
| korean | 333 | 29 | initial | 1152 | 0 | initial |
| malay | 399 | 3 | initial | 903 | 0 | initial |
| polish | 256 | 25 | rerun_20260419 | 982 | 3 | initial |
| portuguese | 246 | 1 | initial | 673 | 1 | initial |
| romanian | 313 | 2 | rerun_20260419 | 1027 | 1 | initial |
| russian | 203 | 4 | initial | 937 | 0 | initial |
| spanish | 251 | 2 | initial | 781 | 1 | initial |
| swedish | 189 | 0 | rerun_20260419 | 848 | 0 | initial |
| thai | 378 | 2 | initial | 893 | 1 | initial |
| turkish | 436 | 23 | initial | 941 | 24 | initial |
| ukrainian | 314 | 41 | rerun_20260419 | 983 | 14 | initial |
| urdu | 580 | 10 | rerun_20260419 | 1087 | 63 | initial |
| vietnamese | 401 | 9 | initial | 905 | 12 | initial |

### Per-row state notes

The following languages show a high `Back WRONG` count from the initial run and were not re-run on 2026-04-19. The number reflects the **pre-correction** state of the wordlist at the time of the initial run. The currently published wordlist in `wordlists/tzur-original/` reflects the post-correction state. Re-running the back-translation pipeline against the current wordlist would not reproduce these counts because the inputs have moved. The per-language correction record is in [`docs/CONSTRUCTION.md`](../docs/CONSTRUCTION.md).

- **czech.** 615 WRONG of 764 suspects, initial run. Pre-correction state. Currently published wordlist is post-correction.

## Reading the numbers

Suspect counts vary widely by language because the threshold flags entries whose machine translation diverges from the canonical English term. A high suspect count is not in itself an accuracy signal: it commonly reflects script distance (Devanagari, Han, Hangul, Hebrew, Thai), morphological complexity, or one-to-many concept mappings between the source and target language. The accuracy signal is the post-review `WRONG` count.

All entries judged `WRONG` in either pass were corrected before publication. The published wordlist therefore reflects the post-correction state. Re-running the pipeline against the published wordlist would not exactly reproduce the historical `WRONG` counts because the inputs have moved; the rerun for 10 languages on 2026-04-19 is what re-running looks like in practice.

## Provenance and reproducibility

- Pipeline source: `audit/translation_pass/` in the TZUR Wallet repository at <https://github.com/osem23/tzur-wallet>. Scripts: `back_translate.py`, `azure_back_translate.py`, `forward_translate.py`, `llm_review.py`, `apply_all_verdicts.py`.
- Translation engines: Google Translate (back-translation), Microsoft Azure Translator (forward-translation).
- LLM verdict layer: see `llm_review.py` for the prompt template and verdict schema.
- Threshold: cosine similarity 0.65. Entries below the threshold are routed to the LLM; entries at or above the threshold are not.
- The `WRONG` counts above are post-review on the suspect set, not over all 2048 entries.
- Re-running the pipeline against current wordlists requires API credentials for both translation engines and a model endpoint for the verdict layer. The wordlists themselves are reproducible from the repository; the verdicts are not, because they depend on stochastic translation and review steps that this report freezes.

## Native-speaker review

Translation-engine validation is not a substitute for native-speaker review. Native-speaker review status per language is tracked in the README. Hebrew is complete (native he); Spanish and Portuguese are peer-reviewed (native es-AR, native pt-BR); the other 27 languages have the two translation passes above and are open to native-speaker contributions via issue or pull request.

## v2 multi-signal validation

In response to a 2026-04-25 external review that flagged v1's audit trail as opaque on two specific points (single-judge LLM verdicts and bulk application of LLM `suggested_replacement` fields), a v2 multi-signal validation pipeline was run over all 30 wordlists. v2 evaluates each entry by three independent mechanisms (blind LLM top-8 generation, LaBSE multilingual embedding similarity, Wiktionary cross-reference) and ranks entries by how many signals confirm them. Full methodology, per-language results, and reviewer-process documentation are in [`docs/V2_VALIDATION.md`](../docs/V2_VALIDATION.md).

The v2 pass produced a per-language tier distribution (HIGH / MEDIUM / LOW / FAIL) and a reviewer-applied correction count. Across the languages where per-entry maintainer review was possible, approximately one in five gate-passing candidates were rejected as polysemy traps or wrong-sense picks; the rate ranges from 0% to roughly 50% per language. For languages outside the maintainer's review territory, the algorithmic gate decided directly. The rate is documented as the known limit of automated cross-validation and the reason v2 does not auto-apply.

The v2 corrections that were applied are reflected in the currently published wordlists. The `WRONG` counts in the v1 table above remain unchanged because they describe historical state at the time of those passes, not the current state of the inputs.
