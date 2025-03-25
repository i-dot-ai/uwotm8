# uwotm8

> u wot m8? Converting American English to British English

[![Release](https://img.shields.io/github/v/release/i-dot-ai/uwotm8)](https://img.shields.io/github/v/release/i-dot-ai/uwotm8)
[![Build status](https://img.shields.io/github/actions/workflow/status/i-dot-ai/uwotm8/main.yml?branch=main)](https://github.com/i-dot-ai/uwotm8/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/i-dot-ai/uwotm8)](https://img.shields.io/github/commit-activity/m/i-dot-ai/uwotm8)
[![License](https://img.shields.io/github/license/i-dot-ai/uwotm8)](https://img.shields.io/github/license/i-dot-ai/uwotm8)

LLMs are fantastic things, but sometimes they need a little help to write in the King's English. This package converts American English to British English.

## Installation

```bash
pip install uwotm8
```

## Quick Start

```python
from uwotm8 import convert_american_to_british_spelling

en_gb_str = convert_american_to_british_spelling("Our American neighbors' dialog can be a bit off-color when you're used to British spelling, you recognize?")
print(en_gb_str)
```

Bosh! You'll get back:

> Our American **neighbours**' **dialogue** can be a bit off-**colour** when you're used to British spelling, you **recognise**?

Or use it on the command line:

```bash
echo "The gray color of the theater is recognized by our neighbors." | uwotm8
# Output: "The grey colour of the theatre is recognised by our neighbours."
```

For complete documentation on all available features and options, see the [Usage Guide](usage.md).

## Features

uwotm8 intelligently preserves words in certain contexts:

- Code blocks (text within backticks)
- URLs and URIs
- Hyphenated terms (e.g., "3-color" remains "3-color" rather than becoming "3-colour")
- Technical terms in the ignore list (e.g., "program" in computing contexts)

For detailed information on how these features work, see the [Implementation Details](modules.md).

## Acknowledgements

Built by the [Incubator for AI (i.AI)](https://ai.gov.uk), part of GDS in the Department for Science, Innovation and Technology (DSIT).

[![i.AI Logo](assets/i-dot-ai.svg#small-logo)](https://ai.gov.uk)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://github.com/i-dot-ai/uwotm8/blob/main/LICENSE)
