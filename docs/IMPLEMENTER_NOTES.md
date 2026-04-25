# Implementer Notes

Non-normative companion to [`BIP-multilingual-mnemonics.md`](BIP-multilingual-mnemonics.md). The BIP draft defines the wire-format and conformance requirements for display wordlists. This document covers the practical wallet-side concerns that fall outside that scope: how to surface portability properly, how to handle restore-time edge cases, and how to run a wordlist artifact through production hygiene.

Nothing here is normative. A wallet that ignores every recommendation in this file can still be BIP-conformant. The point of this file is to capture the operational lessons that would otherwise have to be re-learned in every wallet that ships a display wordlist.

## 1. Backup-time disclosure

The single most important UX moment for a display-mnemonic wallet is the backup screen. The BIP requires the canonical English mnemonic to be available in the same flow. The following framing has held up well in user testing.

**Reference copy.**

> Your seed phrase is shown below in <language>. This phrase is your wallet.
>
> Only the English version of this phrase is guaranteed to restore your wallet in any Bitcoin app. The <language> version restores in this app and any other app that ships the same <language> wordlist; if you switch to an app that does not, you will need the English version.
>
> Write down the English version too. Tap **Show English** to display it.

**Confirmation gate.** Before letting the user past the backup screen, ask the user to confirm they recorded the English version specifically. Wording suggestion:

> I have written down the English version of my seed phrase.

A single checkbox is enough. The point is to defeat the "I'll write the English one later" deferral pattern, which in practice means never.

**Anti-pattern.** Hiding the English version behind two or more taps. Users who do not read English will not seek it out. The English version must be one tap away from the same screen.

## 2. Restore-time input handling

The BIP forbids silent substitution, partial matching, and auto-correction on restore. That leaves a surprisingly large design space for forgiving input. The recommended posture is **forgive at the keyboard, never at the lookup**.

**At the keyboard:**

- Trim leading and trailing whitespace from each token.
- Collapse internal runs of whitespace within the input string into a single space, then tokenize. Users transcribing from paper occasionally insert double spaces; this is recoverable without ambiguity.
- Apply NFC normalization to every token before lookup. The wordlist is NFC at rest; without normalization, a precomposed/decomposed accent mismatch produces a silent lookup failure.
- Strip the BOM if present at the start of the input.

**At the lookup:**

- Each token must exact-match an entry in `native_to_english` after the keyboard-side trims and normalization. A miss is a hard rejection of the entire input.
- Do not try the canonical English wordlist as a fallback for any unrecognized token. A token that matches Spanish but not the loaded Hebrew wordlist is invalid input.
- Do not silently merge or split tokens to satisfy a 12 / 15 / 18 / 21 / 24 word count.

**Did-you-mean suggestions.** Suggesting near-miss alternatives when a token is rejected is fine and recommended. The constraint is that the suggestion is shown to the user as a suggestion, never silently substituted. A typo-tolerant suggestion UI looks like:

> "**çocuk**" is not in the Turkish wordlist. Did you mean **çocuğu**? Tap to use this word.

The user sees the suggestion, decides, and taps. No background correction.

## 3. Compound entries and paper backup

Some languages express a single BIP-39 concept as a multi-word native term. The BIP forbids embedded whitespace inside an entry, so such concepts are stored glued (`hindistancevizi`, `kebunbinatang`, `רופאשיניים`, etc.). This is mechanical and correct, but it is a transcription-time hazard: a user writing the seed on paper may instinctively insert a space.

**At backup time**, when the mnemonic contains a glued compound, surface a hint inline:

> Word 7 is **hindistancevizi**. Write this as one word with no space, even though Turkish would normally space it as "hindistan cevizi".

The dataset in `validation/compound-entries.json` lists which indices in each language's wordlist are glued compounds. A wallet can intersect this with the user's specific mnemonic to know which words need the warning.

**At restore time**, if a user enters a token that contains an embedded space and that token's space-removed form matches a wordlist entry, it is reasonable to suggest the glued form as a did-you-mean. Do not auto-merge. Show the suggestion, let the user confirm.

## 4. Vietnamese and other diacritic-heavy scripts

Vietnamese is the worst-case input language under this convention. Of the 2048 entries, around 99.9% of 12-word mnemonics will contain at least one entry with a tone mark or compound diacritic, and around 43% of entries are glued compounds. Practical implications:

- **Input keyboard.** Use the platform Vietnamese keyboard, not a Latin fallback. The platform keyboard handles Telex/VNI/VIQR composition; a Latin keyboard forces the user to enter precomposed glyphs by codepoint, which is unworkable.
- **NFC normalization.** Apply NFC after every keystroke, not only on submit. Vietnamese input commonly arrives as a base + combining-mark sequence that needs to be composed before display.
- **Compound warnings.** With ~43% of Vietnamese entries glued, a 12-word backup nearly always contains 4-6 compound words. Show the compound hint inline at backup and have the user tap each one to confirm before advancing.

Similar but milder considerations apply to Turkish (29% NFKD-changing entries), Arabic (6%, plus RTL layout), Farsi (5.6% plus ZWNJ), and Thai (5.3%).

## 5. ZWNJ (Persian/Farsi)

The Farsi wordlist contains 556 ZWNJ characters across 534 of 2048 entries. ZWNJ is preserved by NFC and NFKD; it is not a normalization side effect. See `validation/encoding-notes.md` for the canonical statement.

The wallet has two coherent strategies. **Either**:

1. Preserve ZWNJ in the stored wordlist and require ZWNJ in input. Use the platform Persian keyboard, which has a ZWNJ key. This matches what a literate Persian-speaking user expects.

2. Strip ZWNJ from the stored wordlist and strip ZWNJ from input. The display still shows ZWNJ-containing forms (rendered from a separate display-only string), but lookup operates on the stripped form.

Pick one. **Do not mix.** Strategy (2) is more forgiving when users paste from a source that lost ZWNJ during clipboard transit.

## 6. Wordlist artifact governance

The reference registry publishes a stable identifier triple for each wordlist: `language`, `version`, `sha256`, plus `normalization_form`. These are in each mapping file. Recommended wallet behavior:

- **At wallet creation**, persist the triple alongside the encrypted seed in wallet metadata. This pins the exact wordlist version the user backed up under.
- **At restore**, read the persisted triple, fetch (or load from the bundle) the wordlist matching that version, and verify the SHA-256 before use. A mismatch is a hard failure: the restore flow should fall back to canonical English input rather than risk a stale wordlist producing the wrong English mapping.
- **At wordlist update**, never silently switch a user's bound wordlist version. If a newer version has changed entries, treat the older version as the user's authoritative wordlist for that wallet's lifetime, or surface a migration flow that re-displays the new mnemonic and forces a fresh backup.

The registry's `v1.0` tag pins a stable snapshot. Wallet bundles are encouraged to vendor the wordlist files and verify against the published SHA-256 at build time, rather than fetching at runtime.

## 7. Test fixtures

The reference registry ships per-language conformance vectors at `test-vectors/*.json`. Each file contains 14 vectors covering the five canonical BIP-39 entropy lengths.

Recommended fixtures for a wallet test suite, in addition to the canonical vectors:

- **Round trip per language.** For every supported display language, generate a mnemonic, render it in display, parse it back, and confirm the seed matches. Run on every CI build.
- **NFC robustness.** For each test vector, also feed in a decomposed-form variant of the display mnemonic and confirm the wallet normalizes to NFC and recovers correctly.
- **Compound paper-backup hazard.** For each language with glued compounds, construct a vector where the user has erroneously inserted a space inside a compound entry. Confirm the wallet rejects the input cleanly with a useful error, not silently.
- **Cross-wallet portability.** Confirm that the canonical English mnemonic produced by the wallet for a known display mnemonic matches the English mnemonic that any reference BIP-39 implementation produces for the same entropy. The reference decoders at `examples/` are a starting point.

## 8. Out-of-scope concerns

The following are intentionally not addressed by the BIP draft or this document:

- **Multi-language wallets that mix display languages within a single mnemonic.** This is a malformed input under the BIP. A wallet can support multiple display languages, but each individual mnemonic resolves under exactly one display wordlist.
- **Custom wordlists.** A wallet that ships its own non-registry wordlist is free to do so under this convention, provided it satisfies the MUST clauses. The trade-off is that a backup recorded under a custom wordlist depends on the issuing wallet for restore.
- **Hardware wallet display.** Display wordlists are equally applicable to hardware wallets; the only constraint is that the device must render the target script. The BIP makes no assumption about display medium.
