# Governance

This document defines how the registry handles versioning, change management, and integrator communication. The objective is to make the operational behavior of the repository predictable for any wallet that integrates these wordlists.

## Versioning model

The registry uses a single pinned tag, `v1.0`. The tag anchors the commit whose 30 TZUR Original wordlists shipped in the TZUR wallet's first public release and does not move. There is no `v1.0.1`, no `v1.1`, no `v2.0` at the time of writing.

The wordlist tokens at each English index are frozen once they ship in a released wallet build. Users who wrote their backup phrase against those tokens rely on the displayed words matching their handwritten record on restore. Editing a token at a given index after ship would break that contract for any user who created a wallet on the prior corpus. The cryptographic floor (canonical English BIP-39 + PBKDF2-NFKD) keeps funds safe regardless, but the display-layer contract that wallets advertise to users is preserved by treating the shipped corpus as immutable.

This means the `v1.0` SHA-256 values in `mappings/*.json` are stable for integrators that pinned them. Wallets persisting `(language, version, sha256)` alongside seed metadata will see the same triple on every future restore.

If a future TZUR build ever needs a different corpus (a fully reviewed alternative wordlist for a language, a new language addition that requires re-cutting the set, or any other ship-shaping reason), the right move is a new tag (`v2.0`) anchored at a new commit; the existing `v1.0` tag still pins the original corpus for backward compatibility.

## What can still change in this repository

Wordlist token files at `wordlists/tzur-original/*.txt` do not change post-ship. Everything else in the repository may evolve without touching `v1.0`:

- Documentation: BIP draft, governance, construction notes, implementer notes, coverage methodology, README.
- Validator and tooling: `validation/validate_all.py`, CI workflows, the test-vector generator.
- Reference decoders under `examples/`.
- Audit reports, candidate queues, and errata documents.
- Test vectors under `test-vectors/`. These regenerate deterministically from the frozen wordlists; CI enforces byte-identity.
- The `sha256` field in `mappings/*.json` may be recomputed against LF-normalized wordlist bytes if a prior commit captured a hash against CRLF or another non-canonical encoding; that is a documentation correction, not a wordlist change.

A commit that touches the documentation, validator, or example decoders does not move `v1.0`. The tag stays where it is.

## Audit findings on the shipped corpus

Findings from periodic LLM or native-speaker audits that flag wrong-sense or POS-drift entries in shipped wordlists are tracked in writing (audit reports under `docs/`, machine-readable candidate queues under `validation/` when used) but are not applied as token swaps. They become input to a future versioned wordlist re-cut.

The repository's public framing is a gift to the Bitcoin community. Honest documentation of known imperfections, without batch-replacement, is the correct posture; it invites native-speaker pull requests and downstream native-language review without breaking shipped wallets.

## What constitutes a breaking change for integrators

Under the pinned-tag model, the `v1.0` SHA-256 values are stable for the lifetime of the tag. An integrator that pinned the SHA-256 in `mappings/<language>.json` at v1.0 ship time will see the same SHA-256 on every subsequent fetch.

Two narrow cases can still change a mapping's `sha256` field:

- **Mapping integrity correction.** The committed hash was computed against non-canonical bytes (e.g., CRLF on a Windows checkout) and a subsequent commit re-records the hash against the canonical LF form. The wordlist bytes are unchanged; the recorded hash is corrected.
- **Mapping schema change.** A field is added or renamed in the mapping JSON itself (not the wordlist file). The wordlist's SHA-256 does not change; the mapping's own JSON does.

Both are documented in `CHANGELOG.md`. Neither involves a token swap. Integrators that pin both the wordlist file's SHA-256 (computed directly from the `.txt`) and the commit hash will see no drift from documentation-only edits.

## Communication channel

Repository changes are announced through:

1. **`CHANGELOG.md`.** Every commit that touches documentation, the validator, or auxiliary tooling adds a brief entry when the change is integrator-visible.
2. **GitHub release notes.** The `v1.0` release notes describe the shipped corpus; future release notes describe any future versioned corpus.
3. **The TZUR wallet release notes.** TZUR is the reference implementation. The wallet's release notes record any wordlist-corpus change date and corresponding SHA-256 values per language.

Wallets watching the registry can compare the persisted `wordlistSha256` against the registry's current SHA-256 on each app launch and surface a version-mismatch dialog. Under the pinned-tag model, that check should be quiet for the lifetime of `v1.0`; it remains wired in as defense against accidental drift.

## Process for non-wordlist changes

Documentation, validator, tooling, and reference-decoder changes follow the normal PR flow:

1. **Issue or PR opened.** The proposer describes the change, the affected files, and the rationale.
2. **Structural validator passes.** `validation/validate_all.py` runs on the PR (CI-enforced). The PR cannot merge if any check fails.
3. **Test vectors unchanged.** Test vectors regenerate from the frozen wordlists; any non-wordlist change that produces a test-vector diff is a defect to investigate, not an expected outcome.
4. **`CHANGELOG.md` entry added when the change is integrator-visible.** Internal validator refactors do not always need a changelog entry; documentation or schema changes do.
5. **Maintainer approval.** The maintainer (currently @osem23) merges. `v1.0` is not moved.

## Adding a new language

A new language is a corpus-shaping change and cannot land under `v1.0`. The path is:

1. The new language's wordlist passes structural validation.
2. The new language has a mapping JSON with the same schema as existing mappings (including `version`, `sha256`, `normalization_form`).
3. Test vectors are added at `test-vectors/<language>.json` covering the 5/1/2/1/5 distribution across canonical BIP-39 entropy lengths.
4. The new language appears in `examples/python/decode.py`, `examples/javascript/decode.mjs`, and `examples/swift/Decode.swift` as a recognized language string.
5. A new tag (`v2.0` or similar) is cut to anchor the expanded corpus; `v1.0` continues to pin the original 30-language ship.

## Out of scope

This document does not address:

- Cryptographic key management for signing releases. The repository does not currently sign releases; integrators relying on third-party trust should mirror the registry into their own infrastructure with their own signing.
- Insurance against repository takeover. Integrators concerned about supply-chain risk should pin both the SHA-256 and the commit hash in their build system.
- Cross-wallet wordlist discovery. That is a wallet-UX problem, addressed in the BIP draft `§Rationale` and in `docs/IMPLEMENTER_NOTES.md`.

## Cross-references

- BIP draft: `docs/BIP-multilingual-mnemonics.md` (`§Backup and portability policy`, `§Wordlist supply-chain attacks`).
- Wallet-side guidance: `docs/IMPLEMENTER_NOTES.md` §6 "Wordlist artifact governance".
- Mapping schema: every `mappings/*.json` carries `language`, `version`, `sha256`, `normalization_form`.
- Validator behavior: `validation/validate_all.py` enforces SHA-256 and `normalization_form` consistency on every push.
- Change history: `CHANGELOG.md`.
