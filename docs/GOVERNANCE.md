# Governance

This document defines how the registry handles versioning, change management, and integrator communication. The objective is to make the operational behavior of the repository predictable for any wallet that integrates these wordlists.

## Versioning model

The registry uses a single force-moveable tag, `v1.0`. The tag is moved to a new commit whenever a wordlist correction or addition is merged. There is no `v1.1`, `v2.0`, or any other tag at the time of writing.

This is deliberate. The repository has a single maintainer. Cutting versioned tags for every correction creates integration friction (each integrator must decide whether a given correction is worth migrating to) without proportional benefit while the repository is small. The single-tag model keeps the human cost of accepting corrections low.

The model has one important consequence: the version string is decorative, not load-bearing. A correction to the Romanian wordlist on 2026-04-22 did not move the version string from `v1.0` to `v1.1`. It moved the SHA-256 of `wordlists/tzur-original/romanian.txt`. **SHA-256 is the load-bearing identifier for any consumer that needs to detect change.** The mapping schema's `sha256` field is the canonical place to read it.

## What changes the SHA-256

Any byte-level change to a wordlist file produces a new SHA-256. Concrete change classes:

- **Single-token correction.** A native-speaker review or an audit identifies a wrong, awkward, or culturally inappropriate token at index N. The token is replaced. Every other entry stays unchanged. The wordlist file's SHA-256 changes.
- **Full-wordlist replacement.** The wordlist for a language is regenerated from scratch (e.g., a contributor proposes a fully reviewed alternative). All 2048 entries can change. The SHA-256 changes.
- **Normalization-form change.** An entry that was stored in a non-NFC form is normalized. The bytes change. The SHA-256 changes. The CI validator catches non-NFC entries before merge, so this should not happen post-2026-04-25, but the change class is listed for completeness.
- **Line-ending change.** The repository uses LF (`\n`) line endings. A regression that introduces CR-LF would change the SHA-256. The CI validator catches this as a structural error.
- **Mapping-only change.** A change to the JSON mapping file without a wordlist change does not change the wordlist's SHA-256, but it does change the mapping's own JSON. The mapping carries its own integrity field; verify both.

For each change, the corresponding entry in `mappings/<language>.json` is updated so the `sha256` field matches the new wordlist file. The validator at `validation/validate_all.py` enforces this match on every push.

## What constitutes a breaking change for integrators

**Any SHA-256 change is breaking for any wallet that pinned the previous SHA-256.** There is no in-band way for the registry to declare a change non-breaking. The registry cannot know which entries any given wallet displayed to which users. Even a correction that fixes a long-standing bug can break a user who backed up the old display token on paper.

This is why the BIP draft at `docs/BIP-multilingual-mnemonics.md` recommends that wallets persist `(language, version, sha256)` alongside encrypted seed metadata at wallet creation, and surface a mismatch on restore. The user-facing safety net is the canonical English mnemonic, made available by every conformant wallet, which restores in any BIP-39 implementation regardless of wordlist version.

Integrators should pin **the SHA-256, not the version string**. Pinning the version string under the current single-tag model is equivalent to pinning nothing.

## Communication channel

When the registry's `v1.0` tag is force-moved, the change is announced through three channels in order of priority:

1. **`CHANGELOG.md`.** A new entry at the top describes the change, lists the affected languages and the before-and-after SHA-256 for each affected wordlist, and explains the rationale. Integrators watching the repository should treat any commit that touches a wordlist file as a `CHANGELOG.md` update obligation; PRs that change wordlists without updating the changelog should be sent back.
2. **GitHub release notes.** Once cutting GitHub releases is part of the workflow, each force-move of `v1.0` produces a release note pointing at the relevant `CHANGELOG.md` section.
3. **The TZUR wallet release notes.** Because TZUR is the reference implementation, every wordlist change that lands here also lands in TZUR's bundle. TZUR's release notes record the wordlist-version change date and the before-and-after SHA-256 for any affected language.

Wallets watching the registry can compare the persisted `wordlistSha256` against the registry's current SHA-256 on each app launch (or each restore) and surface a version-mismatch dialog. The BIP draft `§Backup and portability policy` SHOULD 3 spells out this expectation.

## Forward compatibility

If the repository's scale, contributor base, or change frequency outgrows the single-tag model, the migration to versioned tags follows this pattern:

1. The current `v1.0` tag is renamed to `v1.0-final` (or similar) and pinned to its current commit.
2. A new versioning policy is added to this document specifying the semantics: e.g., MAJOR for non-backward-compatible mapping schema changes, MINOR for new languages, PATCH for wordlist corrections.
3. New tags follow the new policy.
4. Integrators using `wordlistSha256` continue to work without changes; integrators using only the version string see explicit version transitions instead of silent force-moves.

Until that migration happens, every consumer pins the SHA-256, and no integration code paths should depend on the version string being immutable.

## Process for wordlist changes

A change to any wordlist file lands through the following process:

1. **Issue or PR opened.** The proposer describes the change, the affected language, the affected indices, and the rationale.
2. **Native-speaker review preferred.** For languages with a documented native-speaker reviewer (`README.md` per-language status table), the reviewer signs off on PR. For languages without, the maintainer applies the change with a clearly stated reasoning, and the per-language status remains "pending native review."
3. **Structural validator passes.** `validation/validate_all.py` runs on the PR (CI-enforced). The PR cannot merge if any check fails. This includes the SHA-256 match between the wordlist file and the mapping's `sha256` field.
4. **Mapping updated in lockstep.** Any wordlist change requires a corresponding mapping JSON update. CI fails the PR if the SHA-256 in the mapping does not match the wordlist file's actual SHA-256.
5. **Translation validation report regenerated when warranted.** If the change is large enough to materially affect the translation report (typically a multi-token correction or a full-wordlist replacement), the report is regenerated. Single-token corrections do not require regeneration; the methodology in `validation/translation-validation-report.md` accommodates this.
6. **`CHANGELOG.md` entry added.** A new entry at the top describes the change as defined under "Communication channel" above.
7. **Maintainer approval.** The maintainer (currently @osem23) merges. The `v1.0` tag is force-moved to point at the new HEAD.
8. **TZUR sync.** If the change is significant enough to warrant a wallet update, the TZUR repository pulls in the change in its next release cycle.

## Adding a new language

A new language addition follows the wordlist-change process above, plus:

1. The new language's wordlist passes structural validation.
2. The new language has a mapping JSON with the same schema as existing mappings (including `version`, `sha256`, `normalization_form`).
3. The new language is added to `validation/validate_all.py`'s implicit coverage (the validator iterates the directory, so no code change is required, but the list of expected languages in the README and BIP draft is updated).
4. Test vectors are added at `test-vectors/<language>.json` covering the 5/1/2/1/5 distribution across canonical BIP-39 entropy lengths.
5. The new language appears in `examples/python/decode.py`, `examples/javascript/decode.mjs`, and `examples/swift/Decode.swift` as a recognized language string.

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
