import argparse
import os
import re
import sys
from collections.abc import Generator, Iterable
from importlib.metadata import version
from pathlib import Path
from typing import Any, Optional, Union

from breame.spelling import american_spelling_exists, get_british_spelling

# Add this constant near the top of the file, after imports but before function definitions
CONVERSION_IGNORE_LIST = {
    "filter": "philtre",  # Modern word vs archaic spelling
    "filet": "fillet",  # Common culinary term
    "program": "programme",  # Computing contexts often prefer "program"
    "disk": "disc",  # Computing contexts often prefer "disk"
    "analog": "analogue",  # Technical contexts often prefer "analog"
    "catalog": "catalogue",  # Business contexts often prefer "catalog"
    "plow": "plough",  # Agricultural contexts
    "pajama": "pyjama",  # Commonly used in American form
    "tire": "tyre",  # Automotive contexts often prefer "tire"
    "check": "cheque",  # Different meanings in different contexts
    "gray": "grey",  # Common in color specifications
    "mold": "mould",  # Scientific contexts often prefer "mold"
    "install": "instal",  # British spelling is "instal"
    "connection": "connexion",  # Modern connectivity term
    "draft": "draught",  # Different meanings in different contexts
}


# Then modify the convert_american_to_british_spelling function to check the ignore_list
def convert_american_to_british_spelling(  # noqa: C901
    text: str, strict: bool = False
) -> Any:
    """
    Convert American English spelling to British English spelling.

    Args:
        text: The text to convert.
        strict: Whether to raise an exception if a word cannot be converted.

    Returns:
        The text with American English spelling converted to British English spelling.
    """
    if not text.strip():
        return text
    try:

        def should_skip_word(word: str, pre: str, post: str, match_start: int, match_end: int) -> bool:
            """Check if the word should be skipped for conversion."""
            # Skip if within code blocks
            if "`" in pre or "`" in post:
                return True

            # Skip if word is in the ignore_list
            if word.lower() in CONVERSION_IGNORE_LIST:
                return True

            # Check for hyphenated terms (e.g., "3-color", "x-coordinate")
            # If the word is part of a hyphenated term, we should skip it
            if "-" in pre and pre.rstrip().endswith("-"):
                return True

            # Check for URL/URI context
            line_start = text.rfind("\n", 0, match_start)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1

            line_end = text.find("\n", match_end)
            if line_end == -1:
                line_end = len(text)

            line_context = text[line_start:line_end]

            # Skip if word appears to be in a URL/URI
            return "://" in line_context or "www." in line_context

        def preserve_capitalization(original: str, replacement: str) -> str:
            """Preserve the capitalization from the original word in the replacement."""
            if original.isupper():
                return replacement.upper()
            elif original.istitle():
                return replacement.title()
            return replacement

        def replace_word(match: re.Match) -> Any:
            """
            Replace a word with its British English spelling.

            Args:
                match: The match object.

            Returns:
                The word with its spelling converted to British English.
            """
            # The first group contains any leading punctuation/spaces
            # The second group contains the word
            # The third group contains any trailing punctuation/spaces
            pre, word, post = match.groups()

            if should_skip_word(word, pre, post, match.start(), match.end()):
                return match.group(0)

            if american_spelling_exists(word.lower()):
                try:
                    british = get_british_spelling(word.lower())
                    british = preserve_capitalization(word, british)
                    return pre + british + post
                except Exception:
                    if strict:
                        raise
            return match.group(0)

        # Match any word surrounded by non-letter characters
        # Group 1: Leading non-letters (including empty)
        # Group 2: The word itself (only letters)
        # Group 3: Trailing non-letters (including empty)
        pattern = r"([^a-zA-Z]*?)([a-zA-Z]+)([^a-zA-Z]*?)"
        return re.sub(pattern, replace_word, text)
    except Exception:
        if strict:
            raise
        return text


def convert_stream(stream: Iterable[str], strict: bool = False) -> Generator[str, None, None]:
    """
    Convert American English spelling to British English spelling in a streaming manner.

    Args:
        stream: An iterable of strings (like lines from a file).
        strict: Whether to raise an exception if a word cannot be converted.

    Yields:
        Converted lines of text.
    """
    for line in stream:
        yield convert_american_to_british_spelling(line, strict=strict)


def convert_file(
    src: Union[str, Path],
    dst: Optional[Union[str, Path]] = None,
    strict: bool = False,
    check: bool = False,
) -> bool:
    """
    Convert American English spelling to British English spelling in a file.

    Args:
        src: Source file path.
        dst: Destination file path. If None, content is written back to source file.
        strict: Whether to raise an exception if a word cannot be converted.
        check: If True, only check if changes would be made without modifying files.

    Returns:
        True if changes were made or would be made (if check=True), False otherwise.
    """
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError()

    with open(src_path, encoding="utf-8") as f:
        content = f.read()

    converted = convert_american_to_british_spelling(content, strict=strict)

    # Check if changes were made
    if content == converted:
        return False

    # If check mode, return True to indicate changes would be made
    if check:
        return True

    # Write changes
    if dst is None:
        dst = src
    dst_path = Path(dst)

    # Create directory if it doesn't exist
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(converted)

    return True


def _extract_parameter_names_from_docstring(content: str) -> list[str]:
    """
    Extract parameter names from a docstring's Args section.

    Args:
        content: The docstring content

    Returns:
        List of parameter names
    """
    lines = content.split("\n")
    in_args_section = False
    parameter_names = []

    for _, line in enumerate(lines):
        stripped = line.strip()

        # Check if we're entering the Args section
        if stripped == "Args:" or stripped == "Arguments:":
            in_args_section = True
            continue

        # Check if we're exiting the Args section (empty line or new section)
        if in_args_section and (not stripped or stripped.endswith(":")):
            in_args_section = False
            continue

        # Extract parameter names from the Args section
        if in_args_section and ":" in stripped:
            param_name = stripped.split(":", 1)[0].strip()
            parameter_names.append(param_name)

    return parameter_names


def _create_parameter_ignore_list(parameter_names: list[str]) -> dict[str, str]:
    """
    Create an ignore_list dictionary from parameter names.

    Args:
        parameter_names: List of parameter names

    Returns:
        Dictionary of words to ignore
    """
    temp_ignore_list = {}
    for param in parameter_names:
        # For each parameter, check if it contains words that would be converted
        param_words = re.findall(r"[a-zA-Z]+", param)
        for word in param_words:
            if american_spelling_exists(word.lower()):
                temp_ignore_list[word.lower()] = word.lower()

    return temp_ignore_list


def _convert_with_ignore_list(content: str, temp_ignore_list: dict[str, str], strict: bool = False) -> str:
    """
    Convert content with a temporary ignore list.

    Args:
        content: Text to convert
        temp_ignore_list: Dictionary of words to temporarily ignore
        strict: Whether to raise exceptions on conversion errors

    Returns:
        Converted content
    """
    # Temporarily add our parameter-derived words to the ignore_list
    original_ignore_list = CONVERSION_IGNORE_LIST.copy()
    for word, keep_as in temp_ignore_list.items():
        if word not in CONVERSION_IGNORE_LIST:
            CONVERSION_IGNORE_LIST[word] = keep_as

    # Convert the content with our expanded ignore_list
    converted_content = convert_american_to_british_spelling(content, strict=strict)

    # Restore the original ignore_list
    CONVERSION_IGNORE_LIST.clear()
    CONVERSION_IGNORE_LIST.update(original_ignore_list)

    return str(converted_content)


def convert_python_comments_only(
    src: Union[str, Path],
    dst: Optional[Union[str, Path]] = None,
    strict: bool = False,
    check: bool = False,
) -> bool:
    """
    Convert American English spelling to British English spelling only in Python comments and docstrings.

    Args:
        src: Source file path.
        dst: Destination file path. If None, content is written back to source file.
        strict: Whether to raise an exception if a word cannot be converted.
        check: If True, only check if changes would be made without modifying files.

    Returns:
        True if changes were made or would be made (if check=True), False otherwise.
    """
    src_path = Path(src)
    if not src_path.exists():
        raise FileNotFoundError()

    # Read the file content
    with open(src_path, encoding="utf-8") as f:
        content = f.read()

    # Use a simpler approach with regular expressions for comments
    modified_content = content
    modified = False

    # Handle single-line comments (# comments)
    comment_pattern = r"(#[^\n]*)"

    def replace_comment(match: re.Match[str]) -> str:
        nonlocal modified
        comment = match.group(1)
        prefix = "#"
        comment_text = comment[len(prefix) :]
        converted_text = convert_american_to_british_spelling(comment_text, strict=strict)

        if converted_text != comment_text:
            modified = True
            return prefix + str(converted_text)
        return comment

    modified_content = re.sub(comment_pattern, replace_comment, modified_content)

    # Handle docstrings with special handling for parameter names in docstring Args
    # First, we'll use regex to find triple-quoted strings
    docstring_pattern = r'("""[\s\S]*?"""|"""[\s\S]*?""")'

    def replace_docstring(match: re.Match[str]) -> str:
        nonlocal modified
        docstring = match.group(1)
        quote_style = '"""' if docstring.startswith('"""') else "'''"

        # Extract the content between the triple quotes
        content = docstring[3:-3]

        # Get parameter names from docstring
        parameter_names = _extract_parameter_names_from_docstring(content)

        # Create ignore_list from parameter names
        temp_ignore_list = _create_parameter_ignore_list(parameter_names)

        # Convert with the temporary ignore_list
        converted_content = _convert_with_ignore_list(content, temp_ignore_list, strict)

        if converted_content != content:
            modified = True
            return quote_style + converted_content + quote_style
        return docstring

    modified_content = re.sub(docstring_pattern, replace_docstring, modified_content)

    # If no changes were made or we're just checking, return early
    if not modified or check:
        return modified

    # Write the converted content back to the file
    if dst is None:
        dst = src
    dst_path = Path(dst)

    # Create directory if it doesn't exist
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    return modified


def _process_file(path: Path, strict: bool, check: bool, comments_only: bool) -> bool:
    """
    Process a single file for conversion.

    Args:
        path: File path to process
        strict: Whether to raise errors on conversion failures
        check: Whether to check only without modifying
        comments_only: Whether to convert only comments in Python files

    Returns:
        True if the file was modified or would be modified
    """
    if path.suffix == ".py" and comments_only:
        return convert_python_comments_only(path, strict=strict, check=check)
    else:
        return convert_file(path, strict=strict, check=check)


def process_paths(
    paths: list[Union[str, Path]],
    check: bool = False,
    strict: bool = False,
    comments_only: bool = False,
) -> tuple[int, int]:
    """
    Process multiple files and directories.

    Args:
        paths: list of file and directory paths.
        check: If True, only check if changes would be made without modifying files.
        strict: Whether to raise an exception if a word cannot be converted.
        comments_only: If True, only convert comments in Python files.

    Returns:
        tuple of (number of files processed, number of files changed).
    """
    modified_count = 0
    total_count = 0

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            total_count += 1
            if _process_file(path, strict, check, comments_only):
                modified_count += 1
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = Path(root) / file
                    if file.endswith((".py", ".txt", ".md")):
                        total_count += 1
                        if _process_file(file_path, strict, check, comments_only):
                            modified_count += 1

    return total_count, modified_count


def _handle_file_with_output(args: argparse.Namespace, src_file: Path) -> int:
    """Handle the case where a single file is processed with output option."""
    if src_file.suffix == ".py" and args.comments_only:
        changes_made = convert_python_comments_only(
            src_file,
            args.output,
            strict=args.strict,
            check=args.check,
        )
    else:
        changes_made = convert_file(
            src_file,
            args.output,
            strict=args.strict,
            check=args.check,
        )

    if args.check:
        return 1 if changes_made else 0
    else:
        if changes_made:
            print(f"Converted: {src_file} -> {args.output}")
        else:
            print(f"No changes needed: {src_file}")
        return 0


def main() -> int:  # noqa: C901
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        prog="uwotm8",
        description="Convert American English spelling to British English spelling.",
    )

    parser.add_argument(
        "src",
        nargs="*",
        help="Files or directories to convert. If not provided, reads from stdin.",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write the files back, just return status. Return code 0 means nothing would change. "
        "Return code 1 means some files would be reformatted.",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Raise an exception if a word cannot be converted.",
    )

    parser.add_argument(
        "--comments-only",
        action="store_true",
        help="For Python files, only convert comments and docstrings, leaving code unchanged.",
    )

    parser.add_argument(
        "--include",
        nargs="+",
        default=[".py", ".txt", ".md"],
        help="File extensions to include when processing directories. Default: .py .txt .md",
    )

    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Paths to exclude when processing directories.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file (when processing a single file). If not provided, content is written back to source file.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=version("uwotm8"),
    )

    parser.add_argument(
        "--ignore",
        help="A space-separated string of words to ignore, or a path to a text file containing words to ignore.",
    )

    args = parser.parse_args()

    if args.ignore:
        ignore_path = Path(args.ignore)
        if ignore_path.is_file():
            with open(ignore_path, encoding="utf-8") as f:
                ignore_words = [line.strip() for line in f if line.strip()]
        else:
            ignore_words = args.ignore.split()

        for word in ignore_words:
            CONVERSION_IGNORE_LIST[word.lower()] = word.lower()

    # Process stdin if no paths provided
    if not args.src:
        for line in convert_stream(sys.stdin, strict=args.strict):
            sys.stdout.write(line)
        return 0

    # Process single file with output option
    if len(args.src) == 1 and args.output and Path(args.src[0]).is_file():
        return _handle_file_with_output(args, Path(args.src[0]))

    # Process multiple paths
    if args.output:
        print("Error: --output option can only be used with a single file input")
        return 2

    total, modified = process_paths(args.src, check=args.check, strict=args.strict, comments_only=args.comments_only)

    if args.check:
        if modified > 0:
            print(f"Would reformat {modified} of {total} files")
            return 1
        else:
            print(f"All {total} files would be left unchanged")
            return 0
    else:
        if modified > 0:
            print(f"🇬🇧 Reformatted {modified} of {total} files")
        else:
            print(f"All {total} files left unchanged")
        return 0


if __name__ == "__main__":
    sys.exit(main())
