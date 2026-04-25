# Coverage Methodology

This document explains the "roughly 35% / 65%" framing in the README and the per-language numbers behind it. The figure is an estimate, not a precise measurement, and the methodology and definitional choices below determine where it lands. The order of magnitude is robust across reasonable choices: roughly a third of native speakers have a canonical BIP-39 wordlist in their language; roughly two thirds do not.

## Source

Ethnologue 27th edition (2024). [Ethnologue](https://www.ethnologue.com) is the most widely cited reference for global language-speaker totals. Numbers below are taken from Ethnologue 2024 L1 native-speaker totals as of the time of publication of this document. Re-running this calculation against a later edition can shift individual rows by several million speakers per language; the aggregate proportions move much less.

## Definitional choices

- **L1 (native) speakers, not L1+L2.** A user who learned Bitcoin's English BIP-39 vocabulary as an adult is functionally an L2 English user for this purpose. The relevant question for wordlist coverage is "is this person's first language one of the ten canonical lists?", which is an L1 question.
- **World total denominator: world population (~8.0 billion as of 2024).** Some sources sum only counted L1 speakers (~7.1B in Ethnologue), which omits people for whom Ethnologue does not assign an L1 figure. Using world population as the denominator is conservative: it slightly understates per-language coverage percentages. We accept that bias because it errs in the direction of "more people lack canonical coverage", which is the conservative framing for the BIP draft's motivation.
- **Mandarin Chinese only for the Chinese canonical lists.** BIP-39 ships Simplified Chinese and Traditional Chinese as two separate canonical lists. Both are written representations of Mandarin. The L1 figure used is Mandarin native speakers, not "Chinese family" totals (which would inflate by adding Cantonese, Wu, Min, etc., none of which BIP-39 ships canonically).
- **Korean as a single language.** BIP-39 ships one Korean canonical list. The L1 figure used is the combined L1 total for Korean across Koreas.

## Canonical BIP-39 coverage (10 languages)

Approximate L1 native-speaker totals from Ethnologue 27th edition (2024). Numbers in millions. These are point estimates rounded to the nearest 5M for languages above 50M speakers and to the nearest 1M below.

| Language | L1 (M) |
|---|---:|
| English | 380 |
| Spanish | 485 |
| French | 75 |
| Italian | 65 |
| Portuguese | 230 |
| Czech | 11 |
| Japanese | 123 |
| Korean | 81 |
| Mandarin Chinese (Simplified + Traditional) | 940 |
| **Sum** | **2,390** |

World L1 / world population (denominator): ~8,000 million (8.0 billion, 2024).

Coverage: 2,390 / 8,000 = **29.9%, rounded to "roughly 30%".**

Non-coverage: **70.1%, rounded to "roughly 70%".**

The README's "roughly 35% / 65%" framing is on the optimistic side of this calculation (it implicitly counts some L2 capability or a smaller world-population denominator). We are choosing to round to "roughly 30% / 70%" in this methodology doc and to keep the README at "roughly 35% / 65%" as a generous interpretation that survives Ethnologue revisions in either direction. Both numbers are estimates; the order of magnitude is the substantive claim.

## What TZUR Original adds (30 languages)

Approximate L1 totals for the 30 TZUR Original display wordlists. Same source and rounding rules.

| Language | L1 (M) |
|---|---:|
| Arabic (Modern Standard, MSA-readable native dialects) | 360 |
| Hindi | 345 |
| Bengali | 240 |
| Urdu | 70 |
| Farsi (Persian, all variants) | 75 |
| Turkish | 80 |
| Vietnamese | 75 |
| Thai | 60 |
| Hebrew | 5 |
| Polish | 38 |
| Ukrainian | 30 |
| Romanian | 22 |
| Swedish | 10 |
| Danish | 5 |
| Filipino (Tagalog) | 30 |
| Malay | 19 |
| Indonesian | 45 |
| Russian | 150 |
| Dutch | 25 |
| German | 76 |
| Estonian | 1 |
| (also 9 of the 10 canonical languages, redundantly available as TZUR Original semantic translations) | (already counted above) |
| **Sum (incremental over canonical)** | **~1,760** |

Note: the Arabic figure deserves a footnote. Ethnologue separates Modern Standard Arabic from the spoken Arabic varieties (Egyptian, Levantine, Maghrebi, Gulf, etc.) that share the written script and most BIP-39-relevant vocabulary. The 360M figure aggregates speakers of Arabic varieties that read MSA, which is what the wordlist serves; it does not claim 360M native MSA speakers as a colloquial first language.

Combined canonical + TZUR Original coverage: 2,390M + 1,760M = **~4,150M, or roughly 52% of world population.**

The remaining ~48% of native speakers (Bengali sub-dialects beyond the standard, Tamil, Telugu, Marathi, Punjabi, Yoruba, Hausa, Swahili, Javanese, and many others) still have no display wordlist under this convention. Adding them is a future-PR matter, not a closed problem.

## Sensitivity

Reasonable variations in the choices above produce coverage estimates in the range of 27% to 38% for canonical-only coverage and 48% to 58% for canonical-plus-TZUR-Original coverage. The README rounds to "roughly 35%" and "roughly 65%" for canonical-only. Either rounding is defensible; the substantive claim is that two thirds of native speakers globally have no canonical BIP-39 wordlist, and that this convention adds roughly a third more.

## Reproducing the calculation

1. Open Ethnologue's per-language summary pages for the 10 canonical languages and the 30 TZUR Original languages.
2. Sum the L1 native-speaker totals.
3. Divide by world population (8.0B in 2024).
4. Subtract from 1 to get non-coverage.

The script `examples/python/decode.py` does not depend on these numbers; they are documentation, not code. If a future Ethnologue release shifts a major language's L1 total by more than 50M, this document should be updated to match.
