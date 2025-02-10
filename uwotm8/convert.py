import re

from breame.spelling import american_spelling_exists, get_british_spelling


def convert_american_to_british_spelling(  # noqa: C901
    text: str, strict: bool = False
) -> str:
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

        def replace_word(match: re.Match) -> str:
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


if __name__ == "__main__":  # pragma: no cover
    pass
