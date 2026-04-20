# Reference Implementations

Minimal, self-contained reference implementations of BIP-39 mnemonic decoding for every wordlist in this repository. Each implementation converts a native-language mnemonic into its English equivalent via the index-paired wordlist and derives the 64-byte seed using PBKDF2-HMAC-SHA512 over the NFKD-normalized mnemonic.

All three implementations produce the same seed for the same input. Verified against the test vectors in [`../test-vectors/`](../test-vectors/).

## Python (`python/decode.py`)

Dependencies: Python 3.9+ standard library only.

```bash
python3 python/decode.py <language> "<native mnemonic>" [passphrase]

# Example
python3 python/decode.py arabic "تخلي تخلي تخلي تخلي تخلي تخلي تخلي تخلي تخلي تخلي تخلي حول" TREZOR
```

## JavaScript (`javascript/decode.mjs`)

Dependencies: Node.js 18+ standard library only (`node:crypto`, `node:fs`).

```bash
node javascript/decode.mjs <language> "<native mnemonic>" [passphrase]

# Example
node javascript/decode.mjs hebrew "נטוש נטוש נטוש נטוש נטוש נטוש נטוש נטוש נטוש נטוש נטוש אודות" TREZOR
```

## Swift (`swift/Decode.swift`)

Dependencies: Apple platforms only (Foundation + CommonCrypto for PBKDF2).

```bash
swiftc -O swift/Decode.swift -o decode
./decode <language> "<native mnemonic>" [passphrase]

# Example
./decode english "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about" TREZOR
```

## What these examples demonstrate

1. **Index-paired decoding.** The mapping from a native word to its English equivalent is derivable at runtime by looking up the native word's index in its wordlist and reading the word at the same index in `english.txt`. No separate mapping file is required.
2. **BIP-39 seed derivation.** NFKD normalization of both the mnemonic and the salt (`"mnemonic" + passphrase`) is mandatory. PBKDF2-HMAC-SHA512 with 2048 iterations and a 64-byte output produces the BIP-39 seed.
3. **Portability.** Three implementations in three different languages reach byte-identical seeds for the same inputs. This is the property the test vectors enforce.

## What these examples deliberately omit

- **Checksum validation.** A real wallet must verify that the last `ENT/32` bits of the encoded mnemonic match `SHA-256(entropy)[:ENT/32]`. These examples decode assuming valid input; they do not reject malformed mnemonics.
- **Word autocomplete / typo correction.** Production wallets typically implement prefix matching (BIP-39 suggests 4-character prefixes). These examples require exact word matches.
- **BIP-32 key derivation.** The seed is the input to BIP-32; deriving keys is out of scope here.

For a production implementation, see [TZUR Wallet](https://tzur.live).
