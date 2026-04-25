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

EXPECTED_WORD_COUNT = 2048


def is_nfc(s: str) -> bool:
    return s == unicodedata.normalize("NFC", s)

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
        lang = data.get("language", path.stem)
        wl_path = REPO_ROOT / "wordlists" / "tzur-original" / f"{lang}.txt"
        if not wl_path.is_file():
            error(f"{name}: sha256 declared but no matching wordlist at {wl_path.relative_to(REPO_ROOT)}")
        else:
            actual = hashlib.sha256(wl_path.read_bytes()).hexdigest()
            if actual != data["sha256"]:
                error(f"{name}: sha256 mismatch (declared {data['sha256'][:16]}..., actual {actual[:16]}...)")
    if "normalization_form" in data and data["normalization_form"] != "NFC":
        error(f"{name}: normalization_form is '{data['normalization_form']}', expected 'NFC'")


def validate_test_vector(path: Path):
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

    bad = 0
    for i, v in enumerate(vectors):
        mnemonic = v.get("mnemonic", "") if isinstance(v, dict) else ""
        if mnemonic and not is_nfc(mnemonic):
            bad += 1
            if bad <= 3:
                error(f"{name}: vector {i} mnemonic not in NFC at rest")
    if bad == 0:
        print(f"  Vectors: {len(vectors)}, NFC: OK")


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
