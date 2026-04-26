# Contributing

The repository is public. If you want to contribute a correction or a new language, the process below is how it gets reviewed.

## New Language Wordlists

New languages start with a GitHub issue describing the language and approach. The issue is the coordination point: it prevents duplicate effort and surfaces linguistic decisions early.

### Requirements

Every wordlist must satisfy:

- Exactly **2048 words**, one per line
- **UTF-8** encoding, no BOM, Unix line endings (LF)
- **No duplicate** words
- **No leading or trailing whitespace** on any line
- Words should be common, unambiguous, and easy to write by hand
- Avoid words that are visually similar to each other in the target script

### Process

1. Open an issue describing the language and your approach
2. Fork the repo and create your wordlist in `wordlists/` under the appropriate category
3. Create a bidirectional mapping file in `mappings/` (see existing files for format)
4. Run `python validation/validate_all.py` and confirm it passes
5. Submit a PR referencing the issue

### Mapping File Format

Each mapping file is a JSON object:

```json
{
  "language": "language_name",
  "word_count": 2048,
  "description": "Bidirectional BIP-39 mapping between English and [Language]",
  "english_to_native": {
    "abandon": "native_word_at_index_0",
    "ability": "native_word_at_index_1"
  },
  "native_to_english": {
    "native_word_at_index_0": "abandon",
    "native_word_at_index_1": "ability"
  }
}
```

Mappings are index-based: word at position N in your wordlist maps to word at position N in the English wordlist.

## Corrections

If you find an error in an existing wordlist, open an issue with:

- The language and word in question
- The line number
- What the issue is (typo, ambiguity, Unicode problem)
- Your proposed fix with justification

## Running Validation

```bash
python validation/validate_all.py
```

This checks all wordlists and mappings for compliance. Your PR must pass validation.

## Code of Conduct

Be respectful. Stay technical.
