#!/usr/bin/env python3
"""
Validate all BIP-39 wordlists and mappings in this repository.

Checks:
  - UTF-8 encoding without BOM, Unix line endings
  - Exactly 2048 words per wordlist
  - No duplicate words within a wordlist
  - No leading or trailing whitespace
  - No embedded whitespace within a word, using the full Unicode
    White_Space property (loss-of-funds class under space-tokenized
    paper-backup restore)
  - No embedded hyphen or dash characters
  - NFC at rest (stored form must equal its NFC normalization)
  - Mapping files have correct word count and bidirectional consistency

NFKD changes at rest are expected for many languages (Vietnamese, Turkish,
German, Russian, Arabic, Farsi, Thai). NFKD is applied at PBKDF2 time per
BIP-39, not at storage time, so it is not flagged here.
"""

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

EXPECTED_WORD_COUNT = 2048

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
