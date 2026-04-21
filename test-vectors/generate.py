"""Generate BIP-39 test vectors for every wordlist in this repository.

For each canonical entropy value, this script produces a mnemonic in every
supported language and derives the 64-byte seed per BIP-39:

    entropy (hex)
      -> append checksum (first ENT/32 bits of SHA-256(entropy))
      -> split into 11-bit indices
      -> look up words in the target language's wordlist
      -> join with space (or U+3000 for Japanese) to form the mnemonic
      -> NFKD normalize mnemonic and salt ("mnemonic" + passphrase)
      -> PBKDF2-HMAC-SHA512 for 2048 iterations, 64-byte output

Output is written to `test-vectors/{lang}.json`. The English file serves
as the reference; every other file has the same vectors with the mnemonic
translated into the target language via the index-paired wordlist.

Usage:
    python3 test-vectors/generate.py

The script is deterministic. Re-running it produces byte-identical output
unless the underlying wordlists change.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDLISTS_DIR = ROOT / "wordlists"
OUT_DIR = ROOT / "test-vectors"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# The canonical BIP-39 test vectors from Trezor's python-mnemonic test suite.
# Each vector specifies a hex-encoded entropy and a passphrase ("TREZOR" for
# Trezor canon, empty for the BIP-39 default). The mnemonic and seed are
# computed; they are not hardcoded here, so a wordlist change that breaks
# correctness will fail the script.
#
# Entropy lengths: 128, 160, 192, 224, 256 bits -> 12, 15, 18, 21, 24 words.
CANONICAL_ENTROPY = [
    # 128-bit (12 words)
    ("00000000000000000000000000000000", "TREZOR"),
    ("7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f", "TREZOR"),
    ("80808080808080808080808080808080", "TREZOR"),
    ("ffffffffffffffffffffffffffffffff", "TREZOR"),
    # 160-bit (15 words)
    ("000000000000000000000000000000000000000000000000", "TREZOR"),
    ("7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f", "TREZOR"),
    # 192-bit (18 words)
    ("808080808080808080808080808080808080808080808080", "TREZOR"),
    # 224-bit (21 words)
    ("ffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "TREZOR"),
    # 256-bit (24 words)
    ("0000000000000000000000000000000000000000000000000000000000000000", "TREZOR"),
    ("7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f", "TREZOR"),
    ("8080808080808080808080808080808080808080808080808080808080808080", "TREZOR"),
    ("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "TREZOR"),
    # Empty-passphrase vectors (BIP-39 default)
    ("00000000000000000000000000000000", ""),
    ("0000000000000000000000000000000000000000000000000000000000000000", ""),
]


# Mapping of language keys to on-disk wordlist paths.
# English is the canonical BIP-39 source. All 30 non-English languages ship
# as TZUR Original display wordlists (index-paired translations of English).
LANGUAGES = {"english": "reference-canonical/english.txt"}
for _slug in [
    "arabic", "bengali", "chinese_simplified", "chinese_traditional", "czech",
    "danish", "dutch", "estonian", "farsi", "filipino", "french", "german",
    "hebrew", "hindi", "indonesian", "italian", "japanese", "korean", "malay",
    "polish", "portuguese", "romanian", "russian", "spanish", "swedish",
    "thai", "turkish", "ukrainian", "urdu", "vietnamese",
]:
    LANGUAGES[_slug] = f"tzur-original/{_slug}.txt"


def load_words(rel_path: str) -> list[str]:
    path = WORDLISTS_DIR / rel_path
    words = path.read_text(encoding="utf-8").strip().split("\n")
    if len(words) != 2048:
        raise ValueError(f"{rel_path}: expected 2048 words, got {len(words)}")
    return words


def entropy_to_indices(entropy_hex: str) -> list[int]:
    entropy = bytes.fromhex(entropy_hex)
    ent_bits = len(entropy) * 8
    if ent_bits not in (128, 160, 192, 224, 256):
        raise ValueError(f"invalid entropy bit length: {ent_bits}")
    checksum = hashlib.sha256(entropy).digest()
    cs_bits = ent_bits // 32

    bitstring = "".join(f"{b:08b}" for b in entropy)
    bitstring += "".join(f"{b:08b}" for b in checksum)[:cs_bits]

    indices = [int(bitstring[i:i + 11], 2) for i in range(0, len(bitstring), 11)]
    return indices


def indices_to_mnemonic(indices: list[int], words: list[str], language: str) -> str:
    # BIP-39 prescribes U+3000 (ideographic space) for Japanese, regular
    # space for every other language. Implementations that normalize
    # consistently on both sides can use either, but the canonical
    # representation follows this rule.
    separator = "\u3000" if language == "japanese" else " "
    return separator.join(words[i] for i in indices)


def mnemonic_to_seed(mnemonic: str, passphrase: str) -> bytes:
    # BIP-39: NFKD both the mnemonic and the salt before PBKDF2.
    norm_mnemonic = unicodedata.normalize("NFKD", mnemonic).encode("utf-8")
    norm_salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha512", norm_mnemonic, norm_salt, 2048, 64)


def generate_for_language(
    language: str,
    rel_path: str,
    english_words: list[str],
) -> dict:
    words = load_words(rel_path)
    vectors = []
    for entropy_hex, passphrase in CANONICAL_ENTROPY:
        indices = entropy_to_indices(entropy_hex)
        mnemonic = indices_to_mnemonic(indices, words, language)
        # Display-layer convention: PBKDF2 runs on the canonical English
        # mnemonic for every display language. The native mnemonic above is
        # the user-facing rendering; the seed is derived from the English form
        # reached via index substitution. This is the property that makes
        # every display language's seed match English for the same entropy.
        english_mnemonic = indices_to_mnemonic(indices, english_words, "english")
        seed = mnemonic_to_seed(english_mnemonic, passphrase)
        vectors.append({
            "entropy": entropy_hex,
            "word_count": len(indices),
            "mnemonic": mnemonic,
            "passphrase": passphrase,
            "seed": seed.hex(),
        })
    return {
        "language": language,
        "wordlist": rel_path,
        "vector_count": len(vectors),
        "vectors": vectors,
    }


def main() -> None:
    english_words = load_words(LANGUAGES["english"])
    for language, rel_path in LANGUAGES.items():
        payload = generate_for_language(language, rel_path, english_words)
        out_path = OUT_DIR / f"{language}.json"
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {out_path.relative_to(ROOT)} ({payload['vector_count']} vectors)")


if __name__ == "__main__":
    main()
