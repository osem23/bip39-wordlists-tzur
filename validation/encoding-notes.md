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

- ZWNJ is an invisible character that will be **stripped by NFKD normalization**.
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
