# Encoding and Normalization Notes

## UTF-8

All wordlists in this repository are UTF-8 encoded with Unix-style line endings (LF, `\n`). No BOM (byte order mark) is used.

## NFKD Normalization

BIP-39 specifies that mnemonic sentences must be normalized to **NFKD** (Unicode Normalization Form Compatibility Decomposition) before deriving the seed via PBKDF2.

This is critical for non-ASCII scripts where visually identical characters may have different byte representations.

### What NFKD does

NFKD decomposes characters into their canonical and compatibility equivalents, then reorders combining marks. For example:

- `é` (U+00E9) decomposes to `e` (U+0065) + `́` (U+0301)
- `ñ` (U+00F1) decomposes to `n` (U+006E) + `̃` (U+0303)
- Full-width `Ａ` (U+FF21) normalizes to `A` (U+0041)

### Script-Specific Considerations

#### Hebrew

Hebrew text is right-to-left (RTL). When processing Hebrew wordlists programmatically:

- Do not rely on visual ordering in text editors. Use logical (memory) order.
- Hebrew letters do not have case distinctions.
- Be aware of final forms (e.g., כ/ך, מ/ם, נ/ן, פ/ף, צ/ץ) - these are distinct characters in Unicode and must not be conflated.
- Niqqud (vowel diacritics) are not used in these wordlists. All words are unpointed.

#### Arabic

Arabic is also RTL with contextual letter shaping:

- The same letter may appear differently depending on position (initial, medial, final, isolated). Unicode handles this at the rendering level - the underlying codepoints are the same.
- Hamza variations (أ إ ؤ ئ ء) are distinct characters.
- No tashkeel (diacritics) are used in these wordlists.

#### Farsi (Persian)

Farsi uses the Arabic script extended with four additional characters: پ چ ژ گ.

**Important: ZWNJ (Zero-Width Non-Joiner, U+200C).** The Farsi wordlist contains 556 ZWNJ characters across 534 of 2048 words. ZWNJ is linguistically correct in Farsi - it is used to prevent cursive joining between parts of compound words. This is standard Persian orthography, not an error.

Implementers must be aware:

- ZWNJ (U+200C) is **preserved by NFC and NFKD**. Standard Unicode canonical and compatibility normalization does not strip it. An earlier revision of this document stated the opposite; that was a factual error.
- Stripping ZWNJ for input handling is therefore an explicit transformation, not a normalization side effect. Implementations that strip it must do so by an explicit rule applied to both the wordlist keys and user input.
- When performing word lookup or validation against the Farsi wordlist, implementations must compare using the **same form** - either both with ZWNJ or both without.
- The recommended approach: strip ZWNJ from both the wordlist keys and user input before comparison, then use the original (ZWNJ-containing) form only for display.

#### Thai

Thai script does not use spaces between words in normal text, but each entry in the wordlist is a single word on its own line.

- Thai characters include consonants, vowels (which may appear before, after, above, or below the consonant), and tone marks.
- NFKD normalization affects 109 of 2048 Thai words (5.3%). Implementations must apply NFKD consistently.

#### Vietnamese

Vietnamese uses Latin script with extensive diacritics (e.g., `ă`, `ơ`, `ư`, `ạ`, `ầ`):

- A single Vietnamese character may carry both a base diacritic and a tone mark.
- NFKD decomposition is essential. `ầ` (precomposed) must decompose correctly.
- Sorting follows Vietnamese linguistic conventions, not simple Unicode codepoint order.

#### Japanese

The official BIP-39 Japanese wordlist uses full-width katakana. Ideographic spaces (U+3000) separate words in a mnemonic phrase, not ASCII spaces.

#### Chinese (Simplified and Traditional)

CJK characters are generally stable under NFKD normalization. The primary concern is ensuring the correct variant (simplified vs. traditional) is used consistently.

#### Hindi (Devanagari)

Hindi uses the Devanagari script, which includes dependent vowel signs (matras), the nukta (dot below), and the virama (halant) for consonant clusters:

- Nukta combinations (e.g., क़ = क + ़) may exist in precomposed or decomposed form. NFKD decomposes these.
- Dependent vowels (e.g., कि, कु) are stored as consonant + vowel sign in Unicode, not as separate characters.
- The virama (U+094D) joins consonants into conjuncts. Implementations must preserve these sequences exactly.
- NFKD normalization should be applied consistently, as with all non-Latin scripts.

#### Korean

The official BIP-39 Korean wordlist uses Hangul syllable blocks. NFKD decomposes these into Jamo (individual consonant/vowel components). Implementations must handle this decomposition correctly.

### NFKD Impact Summary

| Language | Words affected by NFKD | % |
|----------|----------------------|---|
| Vietnamese | 2001 | 97.7% |
| Turkish | 595 | 29.1% |
| German | 185 | 9.0% |
| Russian | 181 | 8.8% |
| Arabic | 123 | 6.0% |
| Farsi | 114 | 5.6% |
| Thai | 109 | 5.3% |

All other languages are NFKD-stable.

## Normalization collisions and lossy input folding

A wordlist must never contain two distinct entries that collapse to the same string under the normalization a wallet applies before lookup or derivation. There are two cases, and they are treated very differently.

**NFKD collisions (loss-of-funds class, must be zero).** NFKD is the normalization BIP-39 applies before PBKDF2. If two distinct entries collapsed to the same string under NFKD, the derivation boundary itself would be ambiguous. Across all 30 TZUR Original wordlists there are **zero** NFKD collisions. `validation/validate_all.py` enforces this as a hard error per TZUR Original wordlist, so the property cannot silently regress.

**Lossy-fold ambiguities (input-UX class, reported as warnings).** Some wallets "forgive" input by stripping diacritics or case-folding before matching. That is a lossy transform, and it can merge two genuinely distinct entries. These are not wordlist defects (the entries are distinct under exact NFC match, and distinct under NFKD), but they mark the languages where forgiving input is unsafe. `validation/validate_all.py` reports them as warnings. Examples of distinct entries that merge under diacritic stripping:

| Language | Diacritic-fold collision groups | Example pair |
|---|---:|---|
| Vietnamese | 85 | `được` / `đuốc` → `đuoc` |
| Thai | 46 | `อายุ` / `อาย` |
| Swedish | 17 | `läger` / `lager` |
| Arabic | 11 | `إعلان` / `اعلان` |
| Estonian | 9 | `köök` / `kook` |
| Romanian | 8 | `derivă` / `deriva` |
| French | 7 | `armé` / `arme` |
| Hindi | 5 | `ख़तरा` / `खतरा` |
| Turkish | 5 | `açı` / `acı` |
| Czech | 4 | `ulička` / `ulicka` |
| Japanese | 3 | `まだ` / `また` (combining dakuten) |

(German, Danish, Bengali, Italian, Polish, and Spanish each have 1-2 groups; German has 6 case-fold groups, such as `Grenze` / `grenze`, and Czech 2. Regenerate the current figures by running the validator.)

**The rule for implementers:**

- Wordlists are stored in NFC at rest.
- A wallet may normalize user input (trim, collapse whitespace, NFC) before lookup. NFC and NFKD are safe: they never merge two distinct entries in these wordlists.
- A wallet **must not** silently strip diacritics or case-fold on input as a "did-you-mean" shortcut and then auto-pick one entry. If a lossy transform maps the user's token to more than one wordlist entry, the wallet **must reject the input and ask the user to disambiguate** rather than guessing. Picking one silently can select the wrong index and derive the wrong seed.
- Be especially careful in languages where users habitually type without accents or diacritics (Vietnamese, Thai, the Latin-diacritic languages). A forgiving keyboard layer that drops tone marks is exactly the failure mode these warnings exist to prevent.

This mirrors the BIP draft's Input parsing rule: forgive at the keyboard for unambiguous transforms, never resolve an ambiguous token silently.

## Validation Checklist

When integrating any wordlist:

1. Verify the file contains exactly 2048 lines (no trailing newline producing an empty 2049th entry).
2. Verify UTF-8 encoding without BOM.
3. Verify no duplicate words exist.
4. Verify no leading or trailing whitespace on any line.
5. Strip `\r` (CR) from line endings if consuming on Windows or if `core.autocrlf` is enabled.
6. For Farsi: decide on a ZWNJ strategy (strip for lookup, preserve for display) and apply consistently.
7. Apply NFKD normalization to mnemonics before seed derivation.
8. Test round-trip: generate mnemonic, normalize, derive seed, verify against known test vectors.
