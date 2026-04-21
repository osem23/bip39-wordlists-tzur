---
name: Word correction
about: Report an incorrect or improvable entry in a TZUR Original wordlist
title: "[correction] <language>: <english word> -> <proposed token>"
labels: correction
---

### Language

<!-- e.g., hebrew, spanish, czech -->

### Index

<!-- 0 through 2047, matching the canonical English BIP-39 position. -->

### Current native token

<!-- What `wordlists/tzur-original/<language>.txt` has at this index today. -->

### Proposed replacement

<!-- A single token, 1-16 graphemes, NFC-normalized, no whitespace. -->

### Rationale

<!-- Why the current token is wrong or weak, and why the replacement is better. Register, idiom, cultural neutrality, dialect notes all welcome. -->

### Reviewer context

<!-- Native speaker of this language? Professional translator? Other reference? -->

### Collision check

- [ ] The proposed replacement does not already appear in `wordlists/tzur-original/<language>.txt`.
- [ ] The proposed replacement is NFC-normalized.
- [ ] The proposed replacement has no whitespace.
- [ ] The proposed replacement is 1-16 graphemes long.
