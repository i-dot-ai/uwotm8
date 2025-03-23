# Usage Guide

## Command Line Usage

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
usage: uwotm8 [-h] [--check] [--strict] [--comments-only] [--include INCLUDE [INCLUDE ...]] [--exclude EXCLUDE [EXCLUDE ...]] [-o OUTPUT] [--version] [src ...]

Convert American English spelling to British English spelling.

positional arguments:
  src                   Files or directories to convert. If not provided, reads from stdin.

options:
  -h, --help            show this help message and exit
  --check               Don't write the files back, just return status. Return code 0 means nothing would change. Return code 1 means some files would be reformatted.
  --strict              Raise an exception if a word cannot be converted.
  --comments-only       For Python files, only convert comments and docstrings, leaving code unchanged.
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

Convert only comments and docstrings in Python files:

```bash
uwotm8 --comments-only myproject/src/
```

Only convert specific file types in a directory:

```bash
uwotm8 myproject/ --include .md .rst
```

Exclude specific paths:

```bash
uwotm8 myproject/ --exclude myproject/vendor/ myproject/generated/
```

## Python API Usage

For more fine-grained control, you can use the Python API:

### Convert a String

```python
from uwotm8 import convert_american_to_british_spelling

# Basic usage
text = "The color of the theater is gray."
result = convert_american_to_british_spelling(text)
print(result)  # "The colour of the theatre is grey."

# With strict mode
try:
    result = convert_american_to_british_spelling(text, strict=True)
except Exception as e:
    print(f"Conversion error: {e}")
```

### Convert a File

```python
from uwotm8 import convert_file

# Convert a file in-place
convert_file("document.txt")

# Convert a file and write to a new file
convert_file("document.txt", "document_gb.txt")

# Check if changes would be made without modifying the file
would_change = convert_file("document.txt", check=True)
if would_change:
    print("File would be modified")
else:
    print("No changes needed")
```

### Convert Only Comments and Docstrings in Python Files

```python
from uwotm8 import convert_python_comments_only

# Convert only comments and docstrings in a Python file, preserving code
convert_python_comments_only("script.py")

# Convert comments/docstrings and write to a new file
convert_python_comments_only("script.py", "script_gb.py")

# Check mode
would_change = convert_python_comments_only("script.py", check=True)
if would_change:
    print("Comments/docstrings would be modified")
else:
    print("No changes needed")
```

### Process Multiple Files

```python
from uwotm8 import process_paths

# Process multiple files and directories
total, modified = process_paths(["file1.txt", "directory/"])
print(f"Processed {total} files, modified {modified}")

# Check mode
total, modified = process_paths(["file1.txt", "directory/"], check=True)
print(f"Would modify {modified} of {total} files")

# Process only comments and docstrings in Python files
total, modified = process_paths(["src/"], comments_only=True)
print(f"Modified comments in {modified} of {total} files")
```

### Stream Processing

```python
from uwotm8 import convert_stream

# Process a stream of lines
with open("input.txt", "r") as f:
    for converted_line in convert_stream(f):
        print(converted_line, end="")
```

## Special Cases and Context Handling

uwotm8 includes intelligent handling of various text contexts:

### Python Comments-Only Mode

When using the `--comments-only` option with Python files, only comments and docstrings are converted, leaving actual code unchanged:

```bash
# Input Python file:
# This comment has color in it
def set_color(color_value):
    """Process the color parameter."""
    return color_value  # Return the color

# After running: uwotm8 --comments-only file.py
# This comment has colour in it
def set_color(color_value):
    """Process the colour parameter."""
    return color_value  # Return the colour
```

This is particularly useful for maintaining code functionality while ensuring documentation follows British English spelling conventions.

#### Parameter Name Preservation

When converting Python docstrings, parameter names in docstring sections are preserved in their original form to maintain consistency with the code:

```python
# Original:
def process_data(color_map, flavor_list):
    """Process data.

    Args:
        color_map: A mapping of colors to values.
        flavor_list: A list of flavors to process.
    """
    return color_map

# After conversion with --comments-only:
def process_data(color_map, flavor_list):
    """Process data.

    Args:
        color_map: A mapping of colours to values.
        flavor_list: A list of flavours to process.
    """
    return color_map
```

Notice how "color_map" and "flavor_list" remain unchanged in the parameter names, while descriptive text is converted.

### Hyphenated Terms

Words that are part of hyphenated terms are preserved in their original form. For example:

```bash
echo "The colors are red and blue, but a 3-color system is used." | uwotm8
# Output: "The colours are red and blue, but a 3-color system is used."
```

This is useful for preserving technical terminology and compound adjectives where conversion might be inappropriate.

### Code Blocks

Words within code blocks (surrounded by backticks) are not converted:

```bash
echo "The `setColor(color)` function sets the color." | uwotm8
# Output: "The `setColor(color)` function sets the colour."
```

### URLs and URIs

Words that appear in lines containing URLs or URIs are not converted:

```bash
echo "Visit http://example.com/color-picker to select a color." | uwotm8
# Output: "Visit http://example.com/color-picker to select a colour."
```

### Technical Terms Blacklist

A blacklist of technical terms that shouldn't be converted is maintained:

```bash
echo "This program uses an analog signal processor." | uwotm8
# Output: "This program uses an analog signal processor."
```

Common blacklisted terms include:

- "program" (vs "programme") in computing contexts
- "disk" (vs "disc") in computing contexts
- "analog" (vs "analogue") in technical contexts
- "filet" (vs "fillet") in culinary contexts
