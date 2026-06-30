#!/usr/bin/env python3
"""
Validate all BIP-39 wordlists, mappings, test vectors, and compound entries
in this repository.

Checks:
  - UTF-8 encoding without BOM, Unix line endings
  - Exactly 2048 words per wordlist
  - No duplicate words within a wordlist
  - No leading or trailing whitespace
  - No embedded whitespace within a word, using the full Unicode
    White_Space property (loss-of-funds class under space-tokenized
    paper-backup restore)
  - No embedded hyphen or dash characters
  - NFC at rest for TZUR Original wordlists, all mappings, all test-vector
    display mnemonics, and the native-string fields of compound-entries.json
  - No NFKD collisions within a TZUR Original wordlist: two distinct entries
    must never collapse to the same string under NFKD. NFKD is the BIP-39
    PBKDF2 normalization, so an NFKD collision would be a loss-of-funds-class
    ambiguity at the derivation boundary. This is a hard error.
  - Lossy-fold ambiguities are reported as warnings, not errors: distinct
    entries that become identical when a wallet strips diacritics or
    case-folds user input for "forgiving" entry. These are not wordlist
    defects (the entries are distinct under exact NFC match) but flag the
    languages where a wallet MUST NOT silently strip accents or case on
    input without rejecting the now-ambiguous token (BIP draft, Input
    parsing).
  - Mapping files have correct word count and bidirectional consistency

NFC at rest is enforced wherever a wallet might key into a wordlist or
mapping with NFC-normalized user input. The reference-canonical wordlists
under wordlists/reference-canonical/ are excluded from the NFC check
because the BIP-39 spec ships some of them (French, Spanish, Japanese,
Korean) in NFKD-equivalent form, and this repository preserves them
byte-for-byte.

NFKD changes at rest are expected for many languages (Vietnamese, Turkish,
German, Russian, Arabic, Farsi, Thai). NFKD is applied at PBKDF2 time per
BIP-39, not at storage time, so it is not flagged here.
"""

import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path

# Ensure stdout handles Unicode on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = REPO_ROOT / "wordlists"
MAPPINGS_DIR = REPO_ROOT / "mappings"
TEST_VECTORS_DIR = REPO_ROOT / "test-vectors"
COMPOUND_ENTRIES_PATH = REPO_ROOT / "validation" / "compound-entries.json"

# Reuse the canonical entropy->mnemonic->seed pipeline from the generator so
# this validator and `test-vectors/generate.py` cannot drift apart.
sys.path.insert(0, str(TEST_VECTORS_DIR))
from generate import (  # noqa: E402  (path injection above is intentional)
    entropy_to_indices,
    indices_to_mnemonic,
    mnemonic_to_seed,
)

ENGLISH_WORDLIST_REL = "reference-canonical/english.txt"
_ENGLISH_WORDS_CACHE: list[str] | None = None


def _load_english_words() -> list[str]:
    global _ENGLISH_WORDS_CACHE
    if _ENGLISH_WORDS_CACHE is None:
        path = WORDLISTS_DIR / ENGLISH_WORDLIST_REL
        words = path.read_text(encoding="utf-8").strip().split("\n")
        if len(words) != EXPECTED_WORD_COUNT:
            raise RuntimeError(
                f"english wordlist at {ENGLISH_WORDLIST_REL} has {len(words)} entries, "
                f"expected {EXPECTED_WORD_COUNT}"
            )
        _ENGLISH_WORDS_CACHE = words
    return _ENGLISH_WORDS_CACHE


# BIP-39 entropy length in bytes -> word count
_ENTROPY_BYTES_TO_WORDS = {16: 12, 20: 15, 24: 18, 28: 21, 32: 24}

EXPECTED_WORD_COUNT = 2048


def is_nfc(s: str) -> bool:
    return s == unicodedata.normalize("NFC", s)


def strip_diacritics(s: str) -> str:
    """NFKD-decompose and drop combining marks.

    Approximates what a wallet does if it strips accents/diacritics for
    "forgiving" input. Used only for the lossy-fold collision WARNING, never
    for derivation or exact-match lookup.
    """
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )

errors = []
warnings = []
checked = 0


def error(msg: str):
    errors.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def validate_wordlist(path: Path):
    global checked
    checked += 1
    name = path.relative_to(REPO_ROOT)
    # NFC at rest is a TZUR Original requirement. The reference-canonical
    # wordlists are preserved byte-for-byte as the BIP-39 spec ships them,
    # which for some languages (French, Spanish, Japanese, Korean) is the
    # NFKD-equivalent form, not NFC.
    enforce_nfc = "tzur-original" in path.parts
    print(f"\nValidating wordlist: {name}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        error(f"{name}: Not valid UTF-8")
        return

    # Check for BOM
    if text.startswith("\ufeff"):
        error(f"{name}: Contains UTF-8 BOM")
        text = text[1:]

    lines = text.split("\n")

    # Remove trailing empty line (common in text files)
    if lines and lines[-1] == "":
        lines = lines[:-1]

    # Word count
    if len(lines) != EXPECTED_WORD_COUNT:
        error(f"{name}: Expected {EXPECTED_WORD_COUNT} words, got {len(lines)}")

    # Check each word
    seen = set()
    for i, word in enumerate(lines):
        # Leading/trailing whitespace
        if word != word.strip():
            error(f"{name}: Line {i + 1} has leading/trailing whitespace: '{word}'")

        # Embedded whitespace inside a word is a loss-of-funds class bug:
        # mnemonics are whitespace-tokenized on paper-backup restore, so an
        # internal whitespace character fragments the entry into multiple
        # tokens and the seed becomes unrecoverable. str.isspace() in Python
        # is defined over the full Unicode White_Space property, so this
        # check covers ASCII space, tab, NBSP (U+00A0), the ideographic
        # space (U+3000), and every other White_Space codepoint.
        if any(ch.isspace() for ch in word):
            error(f"{name}: Line {i + 1} contains embedded whitespace (loss-of-funds class): '{word}'")

        # Embedded hyphen or dash: forbidden for paper-backup clarity.
        # Visually-similar codepoints (ASCII hyphen-minus, en-dash, em-dash,
        # non-breaking hyphen, soft hyphen) would cause silent lookup failures
        # on restore when the user transcribes a paper backup.
        for ch, name_ch in (("-", "U+002D hyphen-minus"),
                            ("\u2013", "U+2013 en-dash"),
                            ("\u2014", "U+2014 em-dash"),
                            ("\u2011", "U+2011 non-breaking hyphen"),
                            ("\u00ad", "U+00AD soft hyphen")):
            if ch in word:
                error(f"{name}: Line {i + 1} contains {name_ch}: '{word}'")

        # Duplicates
        if word in seen:
            error(f"{name}: Duplicate word at line {i + 1}: '{word}'")
        seen.add(word)

        # Empty lines
        if not word:
            error(f"{name}: Empty line at {i + 1}")

        # NFC at rest. Stored form must equal its NFC normalization, so that
        # input normalized to NFC before lookup matches without ambiguity.
        if enforce_nfc:
            nfc = unicodedata.normalize("NFC", word)
            if word != nfc:
                error(f"{name}: Line {i + 1} not in NFC at rest: '{word}'")

    print(f"  Words: {len(lines)}, Unique: {len(seen)}")


def validate_normalization_collisions(path: Path):
    """Check for normalization collisions within a TZUR Original wordlist.

    NFKD collisions are a hard error: NFKD is the normalization BIP-39 applies
    before PBKDF2, so two distinct entries that collapse under NFKD would be a
    loss-of-funds-class ambiguity at the derivation boundary. This check is
    expected to pass at zero across all languages and exists as a permanent
    regression guard.

    Diacritic-fold and case-fold collisions are warnings: distinct entries that
    become identical only when a wallet applies a lossy transform (stripping
    accents or case-folding) to user input. They are not wordlist defects; they
    mark the languages where a wallet MUST NOT silently strip accents/case on
    restore without rejecting the now-ambiguous token.
    """
    global checked
    if "tzur-original" not in path.parts:
        return
    checked += 1
    name = path.relative_to(REPO_ROOT)
    print(f"\nValidating normalization collisions: {name}")

    words = path.read_text(encoding="utf-8").strip().split("\n")

    def groups(key):
        buckets: dict[str, list[str]] = {}
        for w in words:
            buckets.setdefault(key(w), []).append(w)
        return [members for members in buckets.values() if len(set(members)) > 1]

    nfkd_groups = groups(lambda w: unicodedata.normalize("NFKD", w))
    if nfkd_groups:
        for g in nfkd_groups[:3]:
            error(f"{name}: NFKD collision (loss-of-funds class): {' / '.join(sorted(set(g)))}")
    else:
        print("  NFKD collisions: none")

    diac_groups = groups(strip_diacritics)
    if diac_groups:
        sample = diac_groups[0]
        warn(
            f"{name}: {len(diac_groups)} diacritic-fold collision group(s) "
            f"(e.g. {' / '.join(sorted(set(sample)))}); a wallet that strips diacritics "
            f"on input must reject the ambiguous token, not silently pick one"
        )

    case_groups = groups(lambda w: w.lower())
    if case_groups:
        sample = case_groups[0]
        warn(
            f"{name}: {len(case_groups)} case-fold collision group(s) "
            f"(e.g. {' / '.join(sorted(set(sample)))}); a wallet that case-folds input "
            f"must reject the ambiguous token, not silently pick one"
        )


def validate_mapping(path: Path):
    global checked
    checked += 1
    name = path.relative_to(REPO_ROOT)
    print(f"\nValidating mapping: {name}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        error(f"{name}: Failed to parse: {e}")
        return

    # Check required fields
    for field in ("language", "word_count", "english_to_native", "native_to_english"):
        if field not in data:
            error(f"{name}: Missing required field '{field}'")
            return

    e2n = data["english_to_native"]
    n2e = data["native_to_english"]

    # Word count
    if data["word_count"] != EXPECTED_WORD_COUNT:
        error(f"{name}: word_count is {data['word_count']}, expected {EXPECTED_WORD_COUNT}")

    if len(e2n) != EXPECTED_WORD_COUNT:
        error(f"{name}: english_to_native has {len(e2n)} entries, expected {EXPECTED_WORD_COUNT}")

    if len(n2e) != EXPECTED_WORD_COUNT:
        error(f"{name}: native_to_english has {len(n2e)} entries, expected {EXPECTED_WORD_COUNT}")

    # Bidirectional consistency
    mismatches = 0
    for eng, native in e2n.items():
        if native not in n2e:
            error(f"{name}: '{native}' in e2n but not in n2e")
            mismatches += 1
        elif n2e[native] != eng:
            error(f"{name}: Bidirectional mismatch: {eng} -> {native} -> {n2e[native]}")
            mismatches += 1

    if mismatches == 0:
        print(f"  Bidirectional: OK ({len(e2n)} pairs)")
    else:
        print(f"  Bidirectional: {mismatches} mismatches")

    # NFC at rest on the native side. e2n values and n2e keys carry the
    # native-script form a wallet would key into after NFC-normalizing
    # user input. A non-NFC entry here would cause silent lookup failures.
    nfc_bad = 0
    for native in e2n.values():
        if not is_nfc(native):
            nfc_bad += 1
    for native in n2e.keys():
        if not is_nfc(native):
            nfc_bad += 1
    if nfc_bad:
        error(f"{name}: {nfc_bad} native-side strings not in NFC at rest")

    # Optional integrity fields (BIP §Display wordlist requirements SHOULD 3).
    # If present, sha256 must match the corresponding TZUR Original wordlist
    # file, and normalization_form must equal "NFC".
    if "sha256" in data:
        # Wordlist files are named by the language's English name (the `name`
        # field / filename stem); `language` is the BCP 47 identifier.
        stem = data.get("name", path.stem)
        wl_path = REPO_ROOT / "wordlists" / "tzur-original" / f"{stem}.txt"
        if not wl_path.is_file():
            error(f"{name}: sha256 declared but no matching wordlist at {wl_path.relative_to(REPO_ROOT)}")
        else:
            actual = hashlib.sha256(wl_path.read_bytes()).hexdigest()
            if actual != data["sha256"]:
                error(f"{name}: sha256 mismatch (declared {data['sha256'][:16]}..., actual {actual[:16]}...)")
    if "normalization_form" in data and data["normalization_form"] != "NFC":
        error(f"{name}: normalization_form is '{data['normalization_form']}', expected 'NFC'")


def validate_test_vector(path: Path):
    """Recompute every test vector from declared entropy and wordlist.

    A committed vector is valid only if it reproduces from the entropy +
    declared wordlist + display-layer convention (PBKDF2 over canonical
    English). The earlier NFC-only check passed even when a vector contained
    a word missing from its declared wordlist; that gap is closed here by
    full recomputation.
    """
    global checked
    checked += 1
    name = path.relative_to(REPO_ROOT)
    print(f"\nValidating test vectors: {name}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        error(f"{name}: Failed to parse: {e}")
        return

    vectors = data.get("vectors", [])
    if not isinstance(vectors, list):
        error(f"{name}: 'vectors' is not a list")
        return

    language = data.get("language")
    wordlist_rel = data.get("wordlist")
    if not isinstance(language, str) or not isinstance(wordlist_rel, str):
        error(f"{name}: missing or invalid 'language'/'wordlist' fields")
        return

    wl_path = WORDLISTS_DIR / wordlist_rel
    if not wl_path.is_file():
        error(f"{name}: declared wordlist not found at {wordlist_rel}")
        return

    try:
        wordlist_words = wl_path.read_text(encoding="utf-8").strip().split("\n")
    except UnicodeDecodeError:
        error(f"{name}: declared wordlist {wordlist_rel} is not valid UTF-8")
        return
    if len(wordlist_words) != EXPECTED_WORD_COUNT:
        error(f"{name}: {wordlist_rel} has {len(wordlist_words)} entries, "
              f"expected {EXPECTED_WORD_COUNT}")
        return

    english_words = _load_english_words()
    wordset = set(wordlist_words)

    nfc_bad = 0
    mismatches = 0
    for i, v in enumerate(vectors):
        if not isinstance(v, dict):
            error(f"{name}: vector {i} is not an object")
            mismatches += 1
            continue

        entropy_hex = v.get("entropy")
        passphrase = v.get("passphrase", "")
        committed_mnemonic = v.get("mnemonic", "")
        committed_word_count = v.get("word_count")
        committed_seed = v.get("seed", "")

        if not isinstance(entropy_hex, str) or not isinstance(committed_mnemonic, str) \
                or not isinstance(passphrase, str) or not isinstance(committed_seed, str):
            error(f"{name}: vector {i} missing/invalid required string fields")
            mismatches += 1
            continue

        try:
            entropy_bytes = bytes.fromhex(entropy_hex)
        except ValueError:
            error(f"{name}: vector {i} entropy is not valid hex")
            mismatches += 1
            continue

        expected_word_count = _ENTROPY_BYTES_TO_WORDS.get(len(entropy_bytes))
        if expected_word_count is None:
            error(f"{name}: vector {i} entropy length {len(entropy_bytes)} bytes is not 16/20/24/28/32")
            mismatches += 1
            continue
        if committed_word_count != expected_word_count:
            error(f"{name}: vector {i} word_count {committed_word_count} != expected {expected_word_count}")
            mismatches += 1
            continue

        # Recompute display-language mnemonic.
        try:
            indices = entropy_to_indices(entropy_hex)
            expected_mnemonic = indices_to_mnemonic(indices, wordlist_words, language)
        except Exception as e:
            error(f"{name}: vector {i} mnemonic recompute failed: {e}")
            mismatches += 1
            continue

        if committed_mnemonic != expected_mnemonic:
            error(f"{name}: vector {i} mnemonic does not match recomputed value from entropy")
            mismatches += 1
            continue

        # Tokenize the committed mnemonic and verify every token is in the wordlist.
        # Whitespace tokenization covers ASCII space and U+3000; both are produced
        # by indices_to_mnemonic depending on language.
        tokens = committed_mnemonic.replace("\u3000", " ").split()
        unknown = [t for t in tokens if t not in wordset]
        if unknown:
            error(f"{name}: vector {i} contains tokens missing from {wordlist_rel}: {unknown[:3]}")
            mismatches += 1
            continue

        # Recompute seed via PBKDF2-NFKD over canonical English mnemonic
        # (display-layer convention: PBKDF2 never sees the native form).
        english_mnemonic = indices_to_mnemonic(indices, english_words, "en")
        recomputed_seed = mnemonic_to_seed(english_mnemonic, passphrase).hex()
        if recomputed_seed != committed_seed.lower():
            error(f"{name}: vector {i} seed does not match recomputed PBKDF2 over English mnemonic")
            mismatches += 1
            continue

        if not is_nfc(committed_mnemonic):
            nfc_bad += 1
            if nfc_bad <= 3:
                error(f"{name}: vector {i} mnemonic not in NFC at rest")

    if mismatches == 0 and nfc_bad == 0:
        print(f"  Vectors: {len(vectors)}, recomputed mnemonic + seed: OK, NFC: OK")


def validate_compound_entries(path: Path):
    global checked
    checked += 1
    name = path.relative_to(REPO_ROOT)
    print(f"\nValidating compound entries: {name}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        error(f"{name}: Failed to parse: {e}")
        return

    bad = 0
    def walk(node):
        nonlocal bad
        if isinstance(node, str):
            if not is_nfc(node):
                bad += 1
        elif isinstance(node, dict):
            for k, v in node.items():
                if not is_nfc(k):
                    bad += 1
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    if bad:
        error(f"{name}: {bad} strings not in NFC at rest")
    else:
        print(f"  Strings: NFC OK")


def main():
    print("=" * 60)
    print("BIP-39 Wordlist Validation")
    print("=" * 60)

    # Validate all wordlists
    for category in sorted(WORDLISTS_DIR.iterdir()):
        if not category.is_dir():
            continue
        for wl in sorted(category.glob("*.txt")):
            validate_wordlist(wl)
            validate_normalization_collisions(wl)

    # Validate all mappings
    for mapping in sorted(MAPPINGS_DIR.glob("*.json")):
        validate_mapping(mapping)

    # Validate all test-vector files
    if TEST_VECTORS_DIR.is_dir():
        for tv in sorted(TEST_VECTORS_DIR.glob("*.json")):
            validate_test_vector(tv)

    # Validate compound-entries.json
    if COMPOUND_ENTRIES_PATH.is_file():
        validate_compound_entries(COMPOUND_ENTRIES_PATH)

    # Summary
    print("\n" + "=" * 60)
    print(f"Files checked: {checked}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print("=" * 60)

    if errors:
        print("\nFAILED")
        sys.exit(1)
    else:
        print("\nPASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
