::: uwotm8.convert.convert_american_to_british_spelling

## Word Context Detection

The `convert_american_to_british_spelling` function includes special handling for various text contexts:

### Hyphenated Terms

Words that are part of hyphenated terms are preserved in their original form. For example:

- "3-color" remains "3-color" (not converted to "3-colour")
- "x-coordinate" remains "x-coordinate" (not converted to "x-coordinate")
- "multi-colored" remains "multi-colored" (not converted to "multi-coloured")

This is useful for preserving technical terminology and compound adjectives where conversion might be inappropriate.

### Code Blocks

Words within code blocks (surrounded by backticks) are not converted, preserving code syntax and variable names.

### URLs and URIs

Words that appear in lines containing URLs or URIs (identified by "://" or "www.") are not converted to avoid breaking links.

### Conversion Blacklist

A blacklist of words that should not be converted is maintained, including technical terms that have different meanings in different contexts:

- "program" vs "programme" (in computing contexts)
- "disk" vs "disc" (in computing contexts)
- "analog" vs "analogue" (in technical contexts)
- And others

## Capitalization Preservation

The function preserves the capitalization pattern of the original word:

- ALL CAPS words remain ALL CAPS
- Title Case words remain Title Case
- lowercase words remain lowercase
