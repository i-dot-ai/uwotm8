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

## Usage

### Basic Usage

Convert a single file:

```bash
uwotm8 example.txt
```

Convert multiple files:

```bash
uwotm8 file1.txt file2.md file3.py
```

Process an entire directory:

```bash
uwotm8 ./my_project/
```

Read from stdin and write to stdout:

```bash
echo "I love the color gray and my favorite food is filet mignon." | uwotm8
# Output: "I love the colour grey and my favourite food is filet mignon."
```

### Command Line Options

```
usage: uwotm8 [-h] [--check] [--strict] [--include INCLUDE [INCLUDE ...]] [--exclude EXCLUDE [EXCLUDE ...]] [-o OUTPUT] [--version] [src ...]

Convert American English spelling to British English spelling.

positional arguments:
  src                   Files or directories to convert. If not provided, reads from stdin.

options:
  -h, --help            show this help message and exit
  --check               Don't write the files back, just return status. Return code 0 means nothing would change. Return code 1 means some files would be reformatted.
  --strict              Raise an exception if a word cannot be converted.
  --include INCLUDE [INCLUDE ...]
                        File extensions to include when processing directories. Default: .py .txt .md
  --exclude EXCLUDE [EXCLUDE ...]
                        Paths to exclude when processing directories.
  -o OUTPUT, --output OUTPUT
                        Output file (when processing a single file). If not provided, content is written back to source file.
  --version             show program's version number and exit
```

### Examples

Check which files would be changed without modifying them:

```bash
uwotm8 --check myproject/
```

Convert a file and write the output to a different file:

```bash
uwotm8 american.txt -o british.txt
```

Only convert specific file types in a directory:

```bash
uwotm8 myproject/ --include .md .rst
```

Exclude specific paths:

```bash
uwotm8 myproject/ --exclude myproject/vendor/ myproject/generated/
```

## How It Works

uwotm8 automatically converts American English spelling to British English spelling in your files. It handles common spelling differences like:

- color → colour
- analyze → analyse
- center → centre
- organize → organise

It intelligently preserves capitalization and avoids converting words in code blocks, URLs, and other contexts where conversion would be inappropriate.

A blacklist of terms that shouldn't be converted (like "program" in computing contexts) is also maintained.

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
x
