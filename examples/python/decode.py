# SPDX-License-Identifier: MIT
"""Minimal reference implementation: decode a BIP-39 mnemonic in any supported
language into its English equivalent and derive the 64-byte seed.

Dependencies: Python 3.9+ standard library only (hashlib, hmac, unicodedata, json).

Usage:
    python3 decode.py "<language>" "<native mnemonic>" [passphrase]

Examples:
    python3 decode.py arabic "تخلي تخلي تخلي ... حول" TREZOR
    python3 decode.py hebrew "נטוש נטוש ... אודות"
    python3 decode.py english "abandon abandon ... about"

The script verifies the round-trip against the BIP-39 wordlists shipped in
this repository. It is written for clarity over performance.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
WORDLISTS = REPO_ROOT / "wordlists"
MAPPINGS = REPO_ROOT / "mappings"

# Directory layout matches the repository README.
# English is the canonical BIP-39 source; all 30 non-English languages ship
# as TZUR Original display wordlists (index-paired translations of English).
LANG_TO_PATH = {"english": "reference-canonical/english.txt"}
for tzur in [
    "arabic", "bengali", "chinese_simplified", "chinese_traditional", "czech",
    "danish", "dutch", "estonian", "farsi", "filipino", "french", "german",
    "hebrew", "hindi", "indonesian", "italian", "japanese", "korean", "malay",
    "polish", "portuguese", "romanian", "russian", "spanish", "swedish",
    "thai", "turkish", "ukrainian", "urdu", "vietnamese",
]:
    LANG_TO_PATH[tzur] = f"tzur-original/{tzur}.txt"


def load_wordlist(language: str) -> list[str]:
    if language not in LANG_TO_PATH:
        raise ValueError(f"unsupported language: {language}")
    path = WORDLISTS / LANG_TO_PATH[language]
    # NFC-normalize on load so the lookup map keys match the form a wallet
    # produces after NFC-normalizing user input. See the BIP draft, "Input
    # parsing" MUST 2: input tokens and the display wordlist must compare
    # in the same Unicode form to avoid silent restore failures on
    # precomposed/decomposed accent pairs.
    return [unicodedata.normalize("NFC", w)
            for w in path.read_text(encoding="utf-8").strip().split("\n")]


def split_mnemonic(mnemonic: str, language: str) -> list[str]:
    # Japanese uses U+3000 as the word separator in BIP-39 canon, but
    # split() on default whitespace handles both cases.
    return mnemonic.strip().split()


def native_to_english(mnemonic: str, language: str) -> str:
    """Return the English form of a mnemonic expressed in `language`.

    Works by looking up each native word in the language wordlist to find
    its index, then reading the word at the same index in english.txt.
    This is equivalent to using `mappings/{language}.json` but avoids a
    separate artifact.
    """
    if language == "english":
        return mnemonic.strip()

    native_words = load_wordlist(language)
    english_words = load_wordlist("english")
    native_to_index = {w: i for i, w in enumerate(native_words)}

    translated = []
    for word in split_mnemonic(mnemonic, language):
        # Match the wordlist's stored Unicode form (NFC) before lookup.
        word_nfc = unicodedata.normalize("NFC", word)
        if word_nfc not in native_to_index:
            raise ValueError(f"word not in {language} wordlist: {word!r}")
        translated.append(english_words[native_to_index[word_nfc]])
    return " ".join(translated)


def validate_checksum(english_mnemonic: str) -> None:
    """Verify the BIP-39 checksum bits embedded in the final word.

    BIP-39 mnemonics carry CS = ENT/32 checksum bits at the tail of the
    concatenated 11-bit word indices. CS = SHA-256(ENT)[:CS_bits]. A reference
    decoder must reject any mnemonic whose checksum does not verify, otherwise
    a single transcription error on the final word silently produces a
    valid-looking-but-wrong seed.
    """
    words = english_mnemonic.strip().split()
    n = len(words)
    if n not in (12, 15, 18, 21, 24):
        raise ValueError(f"invalid mnemonic length: {n} words (must be 12/15/18/21/24)")
    english = load_wordlist("english")
    english_index = {w: i for i, w in enumerate(english)}
    indices = []
    for w in words:
        if w not in english_index:
            raise ValueError(f"word not in English BIP-39 wordlist: {w!r}")
        indices.append(english_index[w])
    bits = "".join(f"{i:011b}" for i in indices)
    ent_len = n * 32 // 3   # 128, 160, 192, 224, 256
    cs_len = ent_len // 32  # 4, 5, 6, 7, 8
    assert len(bits) == ent_len + cs_len
    ent_bits = bits[:ent_len]
    cs_bits = bits[ent_len:]
    ent_bytes = bytes(int(ent_bits[i:i + 8], 2) for i in range(0, ent_len, 8))
    digest = hashlib.sha256(ent_bytes).digest()
    digest_bits = "".join(f"{b:08b}" for b in digest)
    expected_cs = digest_bits[:cs_len]
    if cs_bits != expected_cs:
        raise ValueError(
            "BIP-39 checksum mismatch: the mnemonic does not satisfy BIP-39 "
            "integrity. A single mistyped word commonly causes this."
        )


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """BIP-39 seed derivation. NFKD + PBKDF2-HMAC-SHA512, 2048 iterations."""
    norm_mnemonic = unicodedata.normalize("NFKD", mnemonic).encode("utf-8")
    norm_salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha512", norm_mnemonic, norm_salt, 2048, 64)


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    language = sys.argv[1].lower()
    mnemonic = sys.argv[2]
    passphrase = sys.argv[3] if len(sys.argv) > 3 else ""

    english = native_to_english(mnemonic, language)
    # Verify the BIP-39 checksum on the canonical English form. Catches
    # transcription errors before they propagate into the derived seed.
    validate_checksum(english)
    # Display-layer convention: PBKDF2 runs on the canonical English mnemonic,
    # not on the native-language display form. See docs/BIP-multilingual-mnemonics.md.
    seed = mnemonic_to_seed(english, passphrase)

    print(json.dumps({
        "language": language,
        "mnemonic_input": mnemonic,
        "mnemonic_english": english,
        "passphrase": passphrase,
        "seed": seed.hex(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
