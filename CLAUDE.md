# CLAUDE.md

This file provides guidance to Claude Code when working in `osem23/bip39-wordlists-tzur`.

## What This Repo Is

The public artifact behind the BIP-39 multilingual mnemonic display-layer convention. Holds:

- 30 TZUR Original wordlists (display-layer, index-paired to canonical English).
- 10 canonical BIP-39 wordlists from the Trezor reference (kept under `wordlists/reference-canonical/` for reference only).
- 30 bidirectional `english_to_native` / `native_to_english` mappings.
- Test vectors for every wordlist (entropy → mnemonic → seed).
- BIP draft at `docs/BIP-multilingual-mnemonics.md`.
- Reference decoders in Python, JavaScript, Swift.
- Validator (`validation/validate_all.py`) wired into CI.

The repo is **a gift to the 85% of humanity that doesn't operate in English**. Frame all copy declaratively. Never petition BIP editors.

## Cryptographic Floor

Native wordlists are a **display and input layer** over canonical English BIP-39. Seeds commit to canonical English. PBKDF2 runs on English. Native wordlists carry **no new cryptographic surface**. The risk surface for a wrong native word is UX/PR, not safety/funds.

## Single-Tag Governance

`v1.0` is the only tag and it is **pinned**. It anchors the commit whose wordlists shipped in TZUR 3.1 and does not move. No patch tags (no `v1.0.1`, no `v1.1.0`). sha256 hashes in the mapping manifests are the load-bearing identifier for integrators; the tag is the human-readable anchor for the shipped corpus.

Once a TZUR Original wordlist has shipped in a released wallet build, the literal native tokens at each English index are frozen. Users wrote their backup phrases against those tokens; later edits would break the display-layer contract on restore. Audit findings that flag wrong-sense or POS-drift entries are handled structurally (documentation, candidate queues, governance notes) without changing the shipped tokens themselves.

## Validator + CI

CI runs `validation/validate_all.py` and a generator-determinism gate that re-runs `test-vectors/generate.py` and fails on any diff. Both are in `.github/workflows/validate.yml`.

The validator now recomputes mnemonic and seed for every test vector via the helpers in `test-vectors/generate.py`. Stale vectors fail CI.

Reference decoders (Python/JavaScript/Swift) NFC-normalize wordlist entries on load AND user input tokens before lookup, per the BIP draft's "Input parsing" MUST 2.

## Local Windows Note

On Windows checkout, `validate_all.py` reports `mappings/*.json` sha256 mismatches because the local working tree has CRLF while committed sha256 fields were computed against LF. CI on Linux passes. Not a real defect.

## Native-Speaker Review (by design, not a gap)

27 of 30 wordlists are LLM-validated. Hebrew, Spanish, Portuguese have native review. The 27 unreviewed languages are **structurally not getting native review** — TZUR cannot recruit 27 reviewers and the project's premise (a gift) doesn't require it. If an auditor flags this as a gap, respond that it's by design, the cryptographic floor is English, and corrections are welcomed via PR. Do not frame as "still pending."

## Commit Message Style

Short one-liners. Vague-technical, no "fix"/"mistake"/"stale"/"audit response" framing in messages that will be visible publicly. Examples:

- `Refresh arabic and thai test vectors`
- `Apply NFC normalization to wordlist and input in reference decoders`
- `CI: verify test-vector regeneration is byte-identical`

No emdashes anywhere.

## Global Brain

Cross-project context — North Star, decisions, people, history across the BlockSight ecosystem — lives in the Obsidian vault at `C:/Users/Daniel Osemberg/brain`. Use QMD semantic search to surface context that doesn't live in this repo:

```
qmd --index dani-brain search "<topic>"     # BM25
qmd --index dani-brain query "<topic>"      # semantic + rerank
```
