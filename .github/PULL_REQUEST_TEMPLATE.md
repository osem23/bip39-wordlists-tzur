### Summary

<!-- One-paragraph description of the change. -->

### Type

- [ ] Correction to an existing TZUR Original wordlist entry
- [ ] New TZUR Original language wordlist
- [ ] Documentation or metadata change
- [ ] Validation, examples, or test-vector tooling
- [ ] Other

### Checklist for wordlist or mapping changes

- [ ] `python validation/validate_all.py` passes with zero errors.
- [ ] Every affected wordlist contains exactly 2048 entries, one per line, UTF-8 without BOM, Unix line endings.
- [ ] No duplicate entries in any wordlist.
- [ ] No leading, trailing, or embedded whitespace in any entry.
- [ ] All entries are NFC-normalized.
- [ ] Bidirectional mapping round-trip is consistent against `wordlists/reference-canonical/english.txt`.
- [ ] No entry exceeds 16 graphemes.
- [ ] If new language: the accompanying test vector file at `test-vectors/<language>.json` matches the English seed for each entropy.
- [ ] Native-speaker review status recorded in `docs/CONSTRUCTION.md` review-status matrix.

### Related issues

<!-- Link any issues this PR closes or references. -->
