import argparse
import os
import re
import sys
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, Optional, Union, list, tuple

from breame.spelling import american_spelling_exists, get_british_spelling


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
            # Skip if within code blocks
            if "`" in pre or "`" in post:
                return match.group(0)
            if american_spelling_exists(word.lower()):
                try:
                    british = get_british_spelling(word.lower())
                    # Preserve capitalization
                    if word.isupper():
                        british = british.upper()
                    elif word.istitle():
                        british = british.title()
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


def process_paths(
    paths: list[Union[str, Path]],
    check: bool = False,
    strict: bool = False,
) -> tuple[int, int]:
    """
    Process multiple files and directories.

    Args:
        paths: list of file and directory paths.
        check: If True, only check if changes would be made without modifying files.
        strict: Whether to raise an exception if a word cannot be converted.

    Returns:
        tuple of (number of files processed, number of files changed).
    """
    modified_count = 0
    total_count = 0

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            total_count += 1
            if convert_file(path, strict=strict, check=check):
                modified_count += 1
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".py") or file.endswith(".txt") or file.endswith(".md"):
                        file_path = Path(root) / file
                        total_count += 1
                        if convert_file(file_path, strict=strict, check=check):
                            modified_count += 1

    return total_count, modified_count


def main() -> int:
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
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    # Process stdin if no paths provided
    if not args.src:
        for line in convert_stream(sys.stdin, strict=args.strict):
            sys.stdout.write(line)
        return 0

    # Process single file with output option
    if len(args.src) == 1 and args.output and Path(args.src[0]).is_file():
        changes_made = convert_file(
            args.src[0],
            args.output,
            strict=args.strict,
            check=args.check,
        )

        if args.check:
            return 1 if changes_made else 0
        else:
            if changes_made:
                print(f"Converted: {args.src[0]} -> {args.output}")
            else:
                print(f"No changes needed: {args.src[0]}")
            return 0

    # Process multiple paths
    if args.output:
        print("Error: --output option can only be used with a single file input")
        return 2

    total, modified = process_paths(args.src, check=args.check, strict=args.strict)

    if args.check:
        if modified > 0:
            print(f"Would reformat {modified} of {total} files")
            return 1
        else:
            print(f"All {total} files would be left unchanged")
            return 0
    else:
        if modified > 0:
            print(f"Reformatted {modified} of {total} files")
        else:
            print(f"All {total} files left unchanged")
        return 0


if __name__ == "__main__":
    sys.exit(main())
