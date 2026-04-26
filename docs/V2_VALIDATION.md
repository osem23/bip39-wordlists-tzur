# V2 Multi-Signal Validation

This document describes the v2 validation methodology used on all 30 TZUR Original wordlists in 2026-04. v2 is the live audit-trail mechanism going forward; the v1 back-translation + forward-translation passes documented in [`validation/translation-validation-report.md`](../validation/translation-validation-report.md) remain part of the public record.

## Why v2 exists

External feedback in 2026-04 flagged v1's audit trail as opaque on two specific points:

- v1 used a single LLM (Anthropic Claude) as the verdict layer over Google and Azure translation passes. A single judge against a single bar is structurally weaker than independent signals against independent bars.
- v1 applied many `WRONG`-tier corrections in bulk from the LLM's `suggested_replacement` field. Some of those replacements were sense-shifts the LLM picked because the English word was polysemous (the canonical example: Czech `sister → sestřenice` where `sestřenice` is actually *cousin*).

v2 keeps v1's structural rigor in place (every wordlist still passes `validation/validate_all.py` on every push) and adds three near-orthogonal verification signals on top. Entries are ranked by how many signals confirm them. Entries that fail two or more signals surface for human review before any correction lands. The polysemy class of error that affected v1 is caught by v2 in two ways: the blind-generation prompt removes confirmation bias, and Wiktionary cross-reference catches the mainstream-sense translation that the LLM might have skipped.

## Three signals

Each entry in each wordlist is evaluated by three independent mechanisms. They share no architectural component and fail in different ways, so an entry that passes all three is verified by three near-orthogonal mechanisms rather than three correlated ones.

### Signal 1. Blind LLM generation

For each English BIP-39 word and each target language, ask an LLM to produce the top-8 most common single-word translations of the English word into the target language. The LLM **does not see** our current candidate. The signal is whether our candidate appears in the LLM's top-8.

The blind-generation framing is the core methodological improvement over v1. v1 asked "is X a correct translation of Y?", which primes the LLM to look for reasons to confirm. v2 asks "give me the most common translations of Y", which is a cognitively different task: the LLM has no prior to defend, so its top picks reflect the most-common sense of the English word, not a justification of our pick.

Implementation: `audit/translation_pass_v2/1_blind_generation.py` in the wallet repository. Default model: OpenAI `gpt-4o`. Optional second model: Anthropic `claude-3-5-sonnet-latest`; when both are configured, signal 1 PASS requires the candidate to appear in *both* models' top-8 (strict cross-model recall).

Cache: per `(model, language, english_word)` jsonl. First run is paid; subsequent runs are free.

### Signal 2. Multilingual embedding similarity (LaBSE)

For each (English word, native candidate) pair, embed both into LaBSE (Language-agnostic BERT Sentence Embedding, 471 MB local model) and compute cosine similarity. LaBSE is trained on cross-lingual sentence pairs, so words that mean the same thing across languages cluster tightly in its representation space.

This is the only signal that involves no language-model judgment of any kind. It is purely geometric: a number per pair. Pass threshold is 0.56 (the 5th-percentile of the calibration distribution measured across 8 representative languages on 2026-04-25).

Implementation: `audit/translation_pass_v2/2_embedding_similarity.py`. Local CPU inference, no API. Free after the one-time model download.

### Signal 3. Wiktionary cross-reference

For each English BIP-39 word, fetch the English Wiktionary page and parse the translations table for the target language's ISO code. The signal is whether our native candidate (after diacritic normalization for languages like Russian where Wiktionary entries carry pedagogical stress marks) appears in Wiktionary's translation list.

Wiktionary is community-curated by native speakers. This is the closest signal in the v2 pipeline to a native review pass. It does not ask what an LLM thinks; it asks what human contributors who speak the target language as their first language listed as the translation.

Three states per entry:
- **PASS**: the candidate is in Wiktionary's translations table.
- **FAIL**: the candidate is not in the table, but the table exists for the target language.
- **NA**: Wiktionary has no English entry for this BIP-39 word, or the entry has no translations table for the target language. Not all 30 languages get equal Wiktionary coverage; low-resource languages (Filipino, Estonian, Urdu, Bengali, Farsi) have higher NA rates.

When signal 3 returns NA, the per-entry tier is computed over the two available signals (HIGH = 2/2 PASS, MEDIUM = 1/2 PASS, FAIL = 0/2 PASS).

Implementation: `audit/translation_pass_v2/3_wiktionary_lookup.py`. Wikitext fetched once per English word (cached, ~2048 fetches), then re-parsed per language. Free, throttled at 150 req/min per WMF guidance.

## Tier rules

For each entry, the three signals collapse to a single tier:

When all three signals are present:
- **HIGH**: 3/3 PASS
- **MEDIUM**: 2/3 PASS
- **LOW**: 1/3 PASS
- **FAIL**: 0/3 PASS

When signal 3 is NA (no Wiktionary data for this entry/language):
- **HIGH**: 2/2 PASS
- **MEDIUM**: 1/2 PASS
- **FAIL**: 0/2 PASS

When fewer than two signals are present (rare; signals 1 and 2 always run for every language):
- **INSUFFICIENT**

## Reviewer process

The algorithmic gate alone does not apply corrections. After aggregation, a reviewer (the maintainer, sometimes a native speaker) walks the per-pair triage output and decides per entry. A candidate that meets the gate (LLM top-1 cross-confirmed by Wiktionary, single word, not a duplicate elsewhere in the wordlist) is *eligible* for auto-application. The reviewer's role is to catch:

- **Polysemy traps**: cases where the English word has multiple senses and the gate-passing candidate represents a different sense than the wordlist's intended one. Examples surfaced during the 2026-04 sweep: Spanish `dash → raya` (punctuation dash) when the wordlist sense is `arrojo` (motion-burst dash); Japanese `master → 主人` (household head) when the sense is `名人` (expert); Czech `sister → sestřenice` (which is actually *cousin*).
- **Sense-divergence between paired languages**: e.g., Chinese Simplified and Traditional landing on different senses of "tip". The simplified pick was `提示` (advice) and the traditional pick was `小費` (gratuity). Both are valid, but they should align.
- **Native-review territory**: Hebrew has full native review by the maintainer; Spanish and Portuguese are peer-reviewed by es-AR and pt-BR speakers respectively. For these languages the v2 candidates surface for per-entry decision rather than auto-applying.

The polysemy-filter rate varies widely by language. In the 2026-04 sweep, across the 25 languages where per-entry maintainer review was possible, reviewer rejections ran at approximately one in five gate-passing candidates on average, with per-language rates ranging from 0% (where every gate-passing candidate aligned with the wordlist's intended sense) to roughly 50% (Chinese pairs, Dutch, Portuguese where small candidate sets concentrated reviewer rejections). For the 5 languages outside the maintainer's review territory (Thai, Turkish, Ukrainian, Urdu, Vietnamese), the gate decided directly. This rate is documented as a known limit of automated cross-validation and is the reason v2 does not auto-apply: the gate is a productivity tool for the reviewer, not a replacement for human judgment.

## Per-language outputs

The pipeline produces these artifacts per language under `audit/translation_pass_v2/results/` in the wallet repository:

- `{lang}.signal_1_blind.gpt4o.json`. Per-entry record: candidates from the primary LLM, in_top_k flag, top-match position.
- `{lang}.signal_1_blind.claude35.json`. Same fields but from the secondary LLM, when a second model is configured.
- `{lang}.signal_2_embedding.json`. Per-entry: cosine similarity, embedding pass flag.
- `{lang}.signal_3_wiktionary.json`. Per-entry: status (matched / not in candidates / no translation / english not found), Wiktionary alternatives list, in_wiktionary_translations flag.
- `{lang}.confidence.json`. Final per-entry tier with all signal scores attached, sorted FAIL-first.
- A repository-wide `REPORT.md` and `REPORT.json` aggregating across all 30 languages.

## Per-language sweep results

The sweep ran in alphabetical pairs from 2026-04-25 onward. For each pair, the reviewer triaged the auto-fixable candidates, filtered polysemy traps, and applied the survivors. Per-language counts below.

| Language | Tier (HIGH / MED / LOW / FAIL) | Auto-fixable | Polysemy-filtered | Applied | Notes |
|---|---|---:|---:|---:|---|
| Arabic | 913 / 652 / 349 / 134 | 25 | 0 | 25 | |
| Bengali | 1347 / 546 / 86 / 69 | 7 | 0 | 7 | |
| Chinese (Simplified) | 710 / 1014 / 314 / 10 | 6 | 3 | 3 | tip sense divergence flagged |
| Chinese (Traditional) | 1277 / 447 / 307 / 17 | 10 | 4 | 6 | tip sense divergence flagged |
| Czech | 1501 / 406 / 129 / 12 | 21 (consensus pre-v2) | 12 (duplicates) | 9 (initial) + later swap | corrections applied through a separate construction-and-correction cycle prior to v2 (see `docs/CONSTRUCTION.md`) |
| Danish | 1550 / 391 / 87 / 20 | 6 | 2 | 4 | |
| Dutch | 1571 / 363 / 98 / 16 | 7 | 4 | 3 | habit→habijt (monk's robe) flagged before application |
| Estonian | 1366 / 513 / 101 / 68 | 11 | 2 | 9 (1 dup) | walnut/web wrong-sense flagged |
| Farsi | 839 / 796 / 304 / 109 | 16 | 1 | 15 | heavy de-gluing of compound forms |
| Filipino | 924 / 694 / 207 / 223 | 34 | 6 | 28 | largest single-pair batch |
| French | 1628 / 329 / 79 / 12 | 6 | 3 | 3 | de-gluing for hyphenated forms (puzzle, vault) |
| German | 1463 / 471 / 98 / 16 | 14 | 1 | 13 | |
| Hebrew | 1273 / 574 / 155 / 46 | 10 | 4 (maintainer-rejected) | 6 | full native review by maintainer; per-entry decisions |
| Hindi | 1305 / 561 / 140 / 42 | 11 | 0 | 11 | broken Unicode fix at idx 1048 (loan) |
| Indonesian | 1227 / 533 / 184 / 104 | 18 | 1 | 17 | |
| Italian | 1593 / 351 / 95 / 9 | 3 | 0 | 3 | |
| Japanese | 1216 / 473 / 341 / 18 | 9 | 2 | 7 | script normalization (kanji vs hiragana vs katakana) |
| Korean | 1286 / 595 / 140 / 27 | 3 | 1 | 2 | pitch sense conflict flagged |
| Malay | 1331 / 485 / 138 / 94 | 16 | 2 | 14 | de-gluing pattern (ibujari, ayambelanda, luarbandar) |
| Polish | 1520 / 420 / 97 / 11 | 3 | 0 | 3 | |
| Portuguese | 1628 / 345 / 63 / 12 | 3 | 2 | 1 | conservative; peer-reviewed |
| Romanian | 1443 / 400 / 163 / 42 | 10 | 1 | 9 | de-gluing (împingeputernic, fripturădevită, etc.) |
| Russian | 1602 / 369 / 74 / 3 | 3 | 1 | 2 | smallest FAIL bucket in the sweep |
| Spanish | 1529 / 426 / 82 / 11 | 5 | 0 | 5 (with 3 swaps) | full per-entry review by maintainer; 3 swap pairs needed |
| Swedish | 1568 / 375 / 92 / 13 | 6 | 2 | 4 | slim/slide wrong-sense flagged |
| Thai | 1305 / 541 / 143 / 59 | 11 | 0 | 11 | gate-delegated (non-native to maintainer) |
| Turkish | 1280 / 554 / 169 / 45 | 12 | 0 | 11 (1 duplicate at apply) | gate-delegated; victory/win both proposed `galibiyet`, second skipped |
| Ukrainian | 1585 / 345 / 106 / 12 | 4 | 0 | 4 | gate-delegated; timber de-glue (`будівельнадеревина → лісоматеріал`) |
| Urdu | 1199 / 584 / 168 / 97 | 9 | 0 | 9 | gate-delegated; breeze and pepper de-glue |
| Vietnamese | 334 / 410 / 867 / 437 | 74 | 0 | 69 (5 duplicates at apply) | gate-delegated; large batch driven by glued-syllable de-gluing (Vietnamese natively spaces syllables; the wordlist convention forbids embedded whitespace) |

### Corpus-wide tier distribution

Aggregating all 30 languages × 2048 entries = 61,440 (English, native) pairs:

| Tier | Count | Share |
|---|---:|---:|
| HIGH (3/3 PASS) | 39,313 | 64.0% |
| MEDIUM (2/3 PASS) | 14,963 | 24.4% |
| LOW (1/3 PASS) | 5,376 | 8.7% |
| FAIL (0/3 PASS) | 1,788 | 2.9% |
| **Total** | **61,440** | 100.0% |

The HIGH-tier share is the strongest aggregate signal. Roughly two thirds of all entries across all 30 wordlists are confirmed by all three independent mechanisms. The FAIL-tier share is small in absolute terms but matters for prioritization: every FAIL is a candidate for further review even after the gate-eligible subset is auto-fixed. The full per-entry FAIL/LOW listing per language is in the wallet repository at `audit/translation_pass_v2/results/REPORT.md`.

### Note on gate-delegated languages

For languages outside the maintainer's review territory (Thai, Turkish, Ukrainian, Urdu, Vietnamese in the 2026-04 sweep), per-entry sense-shift review is not possible at the maintainer level, and the algorithmic gate decides. The "Polysemy-filtered = 0" rows for these languages reflect that delegation, not the absence of polysemy risk. Native-speaker contributions for these languages are explicitly invited via PR; a v2 post-application native-speaker review remains the highest-leverage next step for them.

## Recurring patterns observed during the sweep

These show up across languages and are worth naming because they explain why the FAIL/LOW buckets are not noise.

- **Glued-compound de-gluing.** The wordlist forbids embedded whitespace (`docs/BIP-multilingual-mnemonics.md` MUST 4) and embedded hyphens (same), so multi-word native concepts had been concatenated as single orthographic tokens (`hindistancevizi`, `kebunbinatang`, `papelaluminio`, `ibujari`, `ayambelanda`). Several such tokens turned out to have a clean single-word alternative the construction process missed. v2 surfaced these per language; corrections applied where a single-word equivalent existed.
- **POS sharpening.** Many entries shifted from a verb-stem or imperative form to the noun or canonical-form citation that BIP-39 wordlists tend to favor (`hiram → hiramin`, `pamer → pameran`, `bela → pertahanan`, `rungkai → menyelesaikan`).
- **Loanword adoption.** Where a target language has both a native compound and a recognized loanword for a modern concept, the loanword was generally a better single-word fit (`saker → putbol` (Filipino soccer), `monster` (Indonesian monster), `vakum` (Indonesian vacuum), `triggerер` (Russian trigger)).
- **Modern-vs-archaic register.** Some entries shifted from poetic/archaic forms to modern register (Polish `intrata → przychód` for profit; Spanish `recio → fuerte` for strong, where the maintainer overrode the LLM's first pick).
- **Polysemy traps**, as discussed above. The reviewer's rejection rate of ~26% for gate-passing candidates is the explicit limit of automated cross-validation.

## Reproducibility

The pipeline is reproducible per the same constraints as v1: structural validation runs on every push (`validation/validate_all.py`), but signal 1 (LLM blind generation) and signal 3 (Wiktionary fetch) depend on external services whose outputs are not pinned to byte-identical reproducibility. Specifically:

- **Signal 1 (LLM)**: outputs vary per model version. The published artifacts pin the model name (`gpt-4o`) and the system prompt; a re-run with a different model version will produce different top-8 lists. Cache files (`audit/translation_pass_v2/cache/blind/{model}/{lang}.jsonl`) are committable but are intentionally kept in the wallet repository, not the public registry, because they include the model identity at run time.
- **Signal 2 (LaBSE)**: deterministic given a pinned model checkpoint. The `sentence-transformers/LaBSE` checkpoint at the time of this run is content-addressable via Hugging Face. A re-run with the same checkpoint produces the same cosine similarities to within floating-point tolerance.
- **Signal 3 (Wiktionary)**: depends on the live state of `en.wiktionary.org` at fetch time. Wiktionary content is community-curated and updates continuously; a re-run weeks later will see different translations. The published wikitext cache (in the wallet repo, not committed to this registry) freezes the snapshot used for the sweep.

The reviewer process is, by construction, not reproducible. Human judgment about polysemy and sense-shift is what v2 is *for*. The audit trail is the chain of commits that landed each pair, plus this document explaining the reviewer rule.

## Cross-references

- **v1 results**: [`validation/translation-validation-report.md`](../validation/translation-validation-report.md). Back-translation and forward-translation passes against the pre-v2 wordlist state.
- **Construction notes**: [`docs/CONSTRUCTION.md`](CONSTRUCTION.md). Per-language construction process, structural rules, multi-word-concept handling.
- **Governance**: [`docs/GOVERNANCE.md`](GOVERNANCE.md). Versioning model, breaking-change policy, change-management process for wordlist updates.
- **Implementer notes**: [`docs/IMPLEMENTER_NOTES.md`](IMPLEMENTER_NOTES.md). Wallet-side guidance for backup, restore, input handling.
- **BIP draft**: [`docs/BIP-multilingual-mnemonics.md`](BIP-multilingual-mnemonics.md). Informational BIP draft specifying the display-layer wordlist convention.
- **Pipeline source** (wallet repository): `audit/translation_pass_v2/` at <https://github.com/osem23/tzur-wallet>. Scripts: `1_blind_generation.py`, `2_embedding_similarity.py`, `3_wiktionary_lookup.py`, `4_aggregate.py`, `5_report.py`.
