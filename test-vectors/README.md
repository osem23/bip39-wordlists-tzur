# Test Vectors

This directory contains BIP-39 conformance test vectors for every wordlist in the repository.

## What is in each file

One JSON file per language: `{language}.json`. Each file contains a fixed set of canonical entropy values encoded into mnemonics in that language, with the corresponding seed derived per BIP-39.

```json
{
  "language": "arabic",
  "wordlist": "tzur-original/arabic.txt",
  "vector_count": 14,
  "vectors": [
    {
      "entropy": "00000000000000000000000000000000",
      "word_count": 12,
      "mnemonic": "...",
      "passphrase": "TREZOR",
      "seed": "..."
    }
  ]
}
```

## Entropy values

The entropy values are the canonical Trezor BIP-39 test inputs. They cover all five valid entropy lengths (128, 160, 192, 224, 256 bits corresponding to 12, 15, 18, 21, 24 words). Most vectors use the passphrase `"TREZOR"` for historical compatibility; two vectors use the empty passphrase (BIP-39 default).

The same entropy value appears in every language file. The mnemonic differs because each language substitutes its own words at the same indices. The seed differs because PBKDF2 hashes the mnemonic string directly; different bytes produce different seeds. This is consistent with BIP-39 and is why wallets must support the same wordlist on both the sending and restoring device.

## Regeneration

These vectors are produced mechanically by `generate.py`:

```bash
python3 test-vectors/generate.py
```

The script reads every wordlist in `../wordlists/`, derives indices from the entropy, joins the words into mnemonics, and computes the seed with PBKDF2-HMAC-SHA512 over the NFKD-normalized mnemonic. Re-running the script produces byte-identical output unless the wordlists change.

## Usage in your implementation

Treat the JSON files as a conformance harness. For each vector, your implementation should:

1. Encode the entropy bytes into a mnemonic in the target language. Compare to `mnemonic`.
2. Derive the BIP-39 seed from that mnemonic and the passphrase. Compare to `seed`.

If both match for every vector, your BIP-39 encoding and PBKDF2 pipeline is conformant for that language.

## What these vectors do not test

- BIP-32 key derivation. The seed can be used as the BIP-32 master seed, but the test vectors stop at BIP-39.
- Mnemonic validation of arbitrary user input. For that, see `../validation/checksum-tests.json`.
- Edge cases in input normalization (ZWNJ handling for Farsi, ideographic-space handling for Japanese). These are called out in `../validation/encoding-notes.md`.

## Sources

- BIP-39 specification: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
- Trezor python-mnemonic canonical test vectors: https://github.com/trezor/python-mnemonic
