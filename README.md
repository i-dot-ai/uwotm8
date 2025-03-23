# uwotm8

[![Release](https://img.shields.io/github/v/release/i-dot-ai/uwotm8)](https://img.shields.io/github/v/release/i-dot-ai/uwotm8)
[![Build status](https://img.shields.io/github/actions/workflow/status/i-dot-ai/uwotm8/main.yml?branch=main)](https://github.com/i-dot-ai/uwotm8/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/i-dot-ai/uwotm8/branch/main/graph/badge.svg)](https://codecov.io/gh/i-dot-ai/uwotm8)
[![Commit activity](https://img.shields.io/github/commit-activity/m/i-dot-ai/uwotm8)](https://img.shields.io/github/commit-activity/m/i-dot-ai/uwotm8)
[![License](https://img.shields.io/github/license/i-dot-ai/uwotm8)](https://img.shields.io/github/license/i-dot-ai/uwotm8)

Converting American English to British English - a tool to automatically convert American English spelling to British English spelling in your text and code files.

- **Github repository**: <https://github.com/i-dot-ai/uwotm8/>
- **Documentation** <https://i-dot-ai.github.io/uwotm8/>

## Installation

```bash
pip install uwotm8
```

## Quick Start

Convert a single file:

```bash
uwotm8 example.txt
```

Convert only comments and docstrings in Python files:

```bash
uwotm8 --comments-only my_script.py
```

Read from stdin and write to stdout:

```bash
echo "I love the color gray." | uwotm8
# Output: "I love the colour grey."
```

Use in Python code:

```python
from uwotm8 import convert_american_to_british_spelling

en_gb_str = convert_american_to_british_spelling("Our American neighbors' dialog can be a bit off-color.")
print(en_gb_str)
# Output: "Our American neighbours' dialogue can be a bit off-colour."
```

## Features

- Converts common American English spellings to British English
- Preserves words in special contexts (code blocks, URLs, hyphenated terms)
- Maintains a blacklist of technical terms that shouldn't be converted
- Preserves original capitalization patterns
- Supports Python file mode to convert only comments and docstrings, leaving code unchanged

For full documentation, examples, and advanced usage, please visit the [documentation site](https://i-dot-ai.github.io/uwotm8/).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
