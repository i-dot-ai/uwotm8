import os
import sys
import tempfile
from io import StringIO
from unittest.mock import patch
from urllib.parse import urlparse

import pytest

from uwotm8.convert import (
    CONVERSION_BLACKLIST,
    convert_american_to_british_spelling,
    convert_file,
    convert_python_comments_only,
    convert_stream,
    main,
    process_paths,
)


class TestConvertAmericanToBritishSpelling:
    def test_basic_conversion(self):
        """Test basic American to British conversion."""
        assert convert_american_to_british_spelling("anglicize") == "anglicise"
        assert convert_american_to_british_spelling("Let's anglicize this text") == "Let's anglicise this text"

    def test_multiple_words(self):
        """Test conversion of multiple words in a text."""
        text = "The color of the aluminum armor is."
        expected = "The colour of the aluminium armour is."
        assert convert_american_to_british_spelling(text) == expected

        # Note: 'gray' is in the blacklist as 'grey', so it won't be converted automatically
        assert convert_american_to_british_spelling("color") == "colour"
        assert convert_american_to_british_spelling("aluminum") == "aluminium"
        assert convert_american_to_british_spelling("armor") == "armour"

    def test_capitalization_preserved(self):
        """Test that capitalization is preserved during conversion."""
        assert convert_american_to_british_spelling("Color") == "Colour"
        assert convert_american_to_british_spelling("COLOR") == "COLOUR"
        assert convert_american_to_british_spelling("color") == "colour"

    def test_punctuation_and_whitespace(self):
        """Test that punctuation and whitespace are preserved."""
        text = "Hello, I prefer the color blue! What's your favorite color?"
        expected = "Hello, I prefer the colour blue! What's your favourite colour?"
        assert convert_american_to_british_spelling(text) == expected

    def test_empty_string(self):
        """Test conversion of an empty string."""
        assert convert_american_to_british_spelling("") == ""
        assert convert_american_to_british_spelling("   ") == "   "

    def test_no_american_words(self):
        """Test text with no American spelling variants."""
        text = "This text contains no American spelling variants."
        assert convert_american_to_british_spelling(text) == text

    def test_blacklisted_words(self):
        """Test that blacklisted words are not converted."""
        for american, _ in CONVERSION_BLACKLIST.items():
            assert convert_american_to_british_spelling(american) == american

    def test_code_block_skipping(self):
        """Test that words in code blocks are not converted."""
        text = "Normal text with color, but `color` in code block should not change."
        expected = "Normal text with colour, but `color` in code block should not change."
        assert convert_american_to_british_spelling(text) == expected

    def test_url_context_skipping(self):
        """Test that words in URLs are not converted."""
        # Create standalone URLs to test
        url_line = "https://example.com/color"
        assert convert_american_to_british_spelling(url_line) == url_line

        www_line = "http://www.color.com"
        parsed_url = urlparse(www_line)
        assert convert_american_to_british_spelling(www_line) == www_line
        assert parsed_url.hostname == "www.color.com"

        # Test with URL in context - URLs should remain unchanged
        text = "For documentation visit https://example.com/color"
        converted = convert_american_to_british_spelling(text)
        assert "https://example.com/color" in converted

        # Separate test for normal words in different sentences
        text1 = "The color is blue."
        text2 = "Check the website: www.color.com"

        assert convert_american_to_british_spelling(text1) == "The colour is blue."
        assert "www.color.com" in convert_american_to_british_spelling(text2)

    def test_strict_mode(self):
        """Test strict mode behavior with mocked American spelling existence."""
        # This is a simplified test that doesn't actually test the strict mode behavior
        # A more comprehensive test would mock the breame functions
        text = "Let's anglicize this text"
        expected = "Let's anglicise this text"
        assert convert_american_to_british_spelling(text, strict=True) == expected

    def test_words_with_numbers(self):
        """Test words with numbers are not affected."""
        text = "IPv4 and IPv6 addresses like 192.168.1.1 should not be changed."
        assert convert_american_to_british_spelling(text) == text

        # Test that words in hyphenated terms are preserved
        text = "The 3-color design uses the color red."
        result = convert_american_to_british_spelling(text)
        assert "3-color" in result  # Hyphenated term preserved
        assert "colour red" in result  # Regular word converted

        # More hyphenated cases
        text = "x-coordinate and y-coordinate in the center of the dialog"
        result = convert_american_to_british_spelling(text)
        assert "x-coordinate" in result  # Hyphenated term preserved
        assert "y-coordinate" in result  # Hyphenated term preserved
        assert "centre" in result  # Regular word converted
        assert "dialogue" in result  # Regular word converted

    def test_words_with_apostrophes(self):
        """Test that words with apostrophes are handled correctly."""
        assert convert_american_to_british_spelling("color's") == "colour's"
        assert convert_american_to_british_spelling("Color's") == "Colour's"

    def test_multiline_text(self):
        """Test conversion of multiline text."""
        text = """Line 1 with color.
Line 2 with flavor.
Line 3 with behavior."""
        expected = """Line 1 with colour.
Line 2 with flavour.
Line 3 with behaviour."""
        assert convert_american_to_british_spelling(text) == expected


class TestConvertStream:
    def test_stream_conversion(self):
        """Test conversion of a stream of lines."""
        stream = ["Line 1 with color.\n", "Line 2 with flavor.\n", "Line 3 with no changes.\n"]
        expected = ["Line 1 with colour.\n", "Line 2 with flavour.\n", "Line 3 with no changes.\n"]

        result = list(convert_stream(stream))
        assert result == expected

    def test_empty_stream(self):
        """Test conversion of an empty stream."""
        assert list(convert_stream([])) == []

    def test_stream_with_strict_mode(self):
        """Test stream conversion with strict mode."""
        stream = ["This text has color.\n"]
        result = list(convert_stream(stream, strict=True))
        assert result == ["This text has colour.\n"]


class TestConvertFile:
    def test_file_conversion(self):
        """Test conversion of a file."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as src_file:
            src_path = src_file.name
            src_file.write("This text has color and flavor.")

        try:
            # Test with same file overwrite
            changed = convert_file(src_path)
            assert changed is True

            with open(src_path) as f:
                assert f.read() == "This text has colour and flavour."

            # Test with no changes needed
            changed = convert_file(src_path)
            assert changed is False

            # Test with different destination file
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as dst_file:
                dst_path = dst_file.name

            # Modify source back to American spelling
            with open(src_path, "w") as f:
                f.write("This text has color and flavor.")

            changed = convert_file(src_path, dst_path)
            assert changed is True

            with open(dst_path) as f:
                assert f.read() == "This text has colour and flavour."
        finally:
            # Clean up
            os.unlink(src_path)
            if "dst_path" in locals():
                os.unlink(dst_path)

    def test_file_not_found(self):
        """Test behavior when file is not found."""
        with pytest.raises(FileNotFoundError):
            convert_file("/path/to/nonexistent/file.txt")

    def test_check_mode(self):
        """Test check mode behavior."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("This text has color.")

        try:
            # Check mode should not modify the file but return True
            changed = convert_file(temp_path, check=True)
            assert changed is True

            with open(temp_path) as f:
                assert f.read() == "This text has color."

            # No changes needed case
            with open(temp_path, "w") as f:
                f.write("This text has colour.")

            changed = convert_file(temp_path, check=True)
            assert changed is False
        finally:
            os.unlink(temp_path)

    def test_new_directory_creation(self):
        """Test that directories are created if needed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, "source.txt")
            with open(src_path, "w") as f:
                f.write("This text has color.")

            # Create a path with a new subdirectory
            dst_path = os.path.join(temp_dir, "subdir", "output.txt")

            # Directory should not exist yet
            assert not os.path.exists(os.path.dirname(dst_path))

            # Convert file
            convert_file(src_path, dst_path)

            # Directory should be created
            assert os.path.exists(os.path.dirname(dst_path))

            # File should be properly converted
            with open(dst_path) as f:
                assert f.read() == "This text has colour."


class TestConvertPythonCommentsOnly:
    def test_comments_only_conversion(self):
        """Test that only Python comments are converted."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("""# This comment has color and should be converted
def example_function():
    \"\"\"
    This docstring has color and should be converted.
    \"\"\"
    # Another comment with flavor
    variable = "This string has color but should NOT be converted"
    print("Text with color stays the same")
""")

        try:
            # Convert the file
            modified = convert_python_comments_only(temp_path)
            assert modified is True

            # Read the converted file
            with open(temp_path) as f:
                content = f.read()

            # Comments should be converted
            assert "# This comment has colour and should be converted" in content
            assert "# Another comment with flavour" in content

            # Docstring should be converted
            assert "This docstring has colour and should be converted." in content

            # Code should not be converted
            assert 'variable = "This string has color but should NOT be converted"' in content
            assert 'print("Text with color stays the same")' in content

            # Check mode should detect changes but not apply them
            with open(temp_path, "w") as f:
                f.write("# This comment has color\nprint('code with color')")

            modified = convert_python_comments_only(temp_path, check=True)
            assert modified is True

            # File should not be modified in check mode
            with open(temp_path) as f:
                assert f.read() == "# This comment has color\nprint('code with color')"
        finally:
            os.unlink(temp_path)

    def test_multilevel_docstrings(self):
        """Test that nested docstrings are converted properly."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write('''"""
Module docstring with color.

This is a multiline docstring with flavor.
"""

def function():
    """Function docstring with color."""
    # Comment with color
    pass
''')

        try:
            modified = convert_python_comments_only(temp_path)
            assert modified is True

            with open(temp_path) as f:
                content = f.read()

            # Both docstrings should be converted
            assert "Module docstring with colour" in content
            assert "multiline docstring with flavour" in content
            assert "Function docstring with colour" in content

            # Comment should be converted
            assert "# Comment with colour" in content
        finally:
            os.unlink(temp_path)

    def test_docstring_argument_names_preservation(self):
        """Test that argument names in docstrings are not converted."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write('''def process_data(color_map, flavor_list, center_point):
    """Process data using various parameters.

    Args:
        color_map: A mapping of colors to values. The colors in this map determine output.
        flavor_list: A list of flavors to process.
        center_point: The center point for calculations.

    This function will analyze the color data and output results centered around
    the center_point. The flavor affects how we analyze the color.
    """
    # This comment has color and flavor
    return color_map, flavor_list
''')

        try:
            # Convert the file
            modified = convert_python_comments_only(temp_path)
            assert modified is True

            # Read the converted file
            with open(temp_path) as f:
                content = f.read()

            # Verify that parameter names in Args section are preserved
            assert "color_map: A mapping of colours to values" in content
            assert "The colours in this map determine output" in content
            assert "flavor_list: A list of flavours to process" in content
            assert "center_point: The center point for calculations" in content  # Parameter name preserved

            # Verify that parameter names when used as code references remain unchanged
            assert "the center_point" in content  # Parameter name preserved in reference
            assert (
                "analyse the color data" in content
            )  # "analyse" converted but "color" preserved in text since it's a param name
            assert "The flavor affects" in content  # "flavor" preserved in text since it's a param name

            # Verify that function parameters in the definition are not modified
            assert "def process_data(color_map, flavor_list, center_point):" in content

            # Verify that comment is converted
            assert "# This comment has colour and flavour" in content

            # Verify that return variables are not modified
            assert "return color_map, flavor_list" in content
        finally:
            os.unlink(temp_path)


class TestProcessPaths:
    def test_process_single_file(self):
        """Test processing a single file."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("This text has color.")

        try:
            total, modified = process_paths([temp_path])
            assert total == 1
            assert modified == 1

            with open(temp_path) as f:
                assert f.read() == "This text has colour."

            # Run again with no changes expected
            total, modified = process_paths([temp_path])
            assert total == 1
            assert modified == 0
        finally:
            os.unlink(temp_path)

    def test_process_directory(self):
        """Test processing a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a few test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.py")
            file3_path = os.path.join(temp_dir, "ignored.log")  # Should be ignored

            with open(file1_path, "w") as f:
                f.write("This text has color.")

            with open(file2_path, "w") as f:
                f.write("# This comment has color.")

            with open(file3_path, "w") as f:
                f.write("This log has color but should be ignored.")

            total, modified = process_paths([temp_dir])
            assert total == 2  # Only .txt and .py files
            assert modified == 2

            with open(file1_path) as f:
                assert f.read() == "This text has colour."

            with open(file2_path) as f:
                assert f.read() == "# This comment has colour."

            with open(file3_path) as f:
                assert f.read() == "This log has color but should be ignored."

    def test_check_mode(self):
        """Test check mode in process_paths."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("This text has color.")

        try:
            total, modified = process_paths([temp_path], check=True)
            assert total == 1
            assert modified == 1

            # File should not be modified
            with open(temp_path) as f:
                assert f.read() == "This text has color."
        finally:
            os.unlink(temp_path)

    def test_comments_only_mode(self):
        """Test comments_only mode in process_paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a Python file
            py_file_path = os.path.join(temp_dir, "script.py")
            with open(py_file_path, "w") as f:
                f.write("""# Comment with color
variable = "String with color"
# Another comment with flavor
""")

            # Create a text file
            txt_file_path = os.path.join(temp_dir, "document.txt")
            with open(txt_file_path, "w") as f:
                f.write("This text has color.")

            # Process with comments_only=True
            total, modified = process_paths([temp_dir], comments_only=True)
            assert total == 2
            assert modified == 2

            # Python file should have only comments converted
            with open(py_file_path) as f:
                py_content = f.read()
                assert "# Comment with colour" in py_content
                assert 'variable = "String with color"' in py_content
                assert "# Another comment with flavour" in py_content

            # Text file should be fully converted (not affected by comments_only)
            with open(txt_file_path) as f:
                assert f.read() == "This text has colour."

    def test_process_multiple_paths(self):
        """Test processing of multiple mixed paths."""
        with tempfile.TemporaryDirectory() as temp_dir1, tempfile.TemporaryDirectory() as temp_dir2:
            # Create files in first directory
            file1_path = os.path.join(temp_dir1, "file1.txt")
            with open(file1_path, "w") as f:
                f.write("This text has color.")

            # Create files in second directory
            file2_path = os.path.join(temp_dir2, "file2.py")
            with open(file2_path, "w") as f:
                f.write("# This comment has color.")

            # Create a standalone file
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as temp_file:
                file3_path = temp_file.name
                temp_file.write("This document has flavor.")

            try:
                # Process all three paths
                total, modified = process_paths([temp_dir1, temp_dir2, file3_path])

                assert total == 3
                assert modified == 3

                # Verify conversions
                with open(file1_path) as f:
                    assert f.read() == "This text has colour."

                with open(file2_path) as f:
                    assert f.read() == "# This comment has colour."

                with open(file3_path) as f:
                    assert f.read() == "This document has flavour."
            finally:
                if os.path.exists(file3_path):
                    os.unlink(file3_path)


class TestMainFunction:
    def test_stdin_processing(self):
        """Test processing from stdin."""
        input_stream = StringIO("This text has color.")
        expected_output = "This text has colour."

        with (
            patch.object(sys, "stdin", input_stream),
            patch.object(sys, "stdout", StringIO()) as fake_output,
            patch.object(sys, "argv", ["uwotm8"]),
        ):  # Fix for the test failing due to pytest args
            exit_code = main()
            assert exit_code == 0
            assert fake_output.getvalue() == expected_output

    def test_single_file_with_output(self):
        """Test processing a single file with output option."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as src_file:
            src_path = src_file.name
            src_file.write("This text has color.")

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as dst_file:
            dst_path = dst_file.name

        try:
            with (
                patch.object(sys, "argv", ["uwotm8", src_path, "-o", dst_path]),
                patch.object(sys, "stdout", StringIO()) as fake_output,
            ):
                exit_code = main()
                assert exit_code == 0
                assert "Converted:" in fake_output.getvalue()

            with open(dst_path) as f:
                assert f.read() == "This text has colour."
        finally:
            os.unlink(src_path)
            os.unlink(dst_path)

    def test_check_mode_multiple_files(self):
        """Test check mode with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a few test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("This text has color.")

            with open(file2_path, "w") as f:
                f.write("This text has flavor.")

            with (
                patch.object(sys, "argv", ["uwotm8", temp_dir, "--check"]),
                patch.object(sys, "stdout", StringIO()) as fake_output,
            ):
                exit_code = main()
                assert exit_code == 1  # Should indicate changes would be made
                assert "Would reformat" in fake_output.getvalue()

            # Files should not be modified
            with open(file1_path) as f:
                assert f.read() == "This text has color."

            with open(file2_path) as f:
                assert f.read() == "This text has flavor."

    def test_output_option_with_multiple_files(self):
        """Test validation of output option with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a few test files
            file1_path = os.path.join(temp_dir, "file1.txt")
            file2_path = os.path.join(temp_dir, "file2.txt")

            with open(file1_path, "w") as f:
                f.write("This text has color.")

            with open(file2_path, "w") as f:
                f.write("This text has flavor.")

            # This should return error code 2
            with (
                patch.object(sys, "argv", ["uwotm8", file1_path, file2_path, "-o", "output.txt"]),
                patch.object(sys, "stdout", StringIO()) as fake_output,
            ):
                exit_code = main()
                assert exit_code == 2
                assert "Error: --output option can only be used with a single file input" in fake_output.getvalue()

    def test_strict_mode_flag(self):
        """Test strict mode flag in main."""
        input_stream = StringIO("This text has color.")
        expected_output = "This text has colour."

        with (
            patch.object(sys, "stdin", input_stream),
            patch.object(sys, "stdout", StringIO()) as fake_output,
            patch.object(sys, "argv", ["uwotm8", "--strict"]),
        ):
            exit_code = main()
            assert exit_code == 0
            assert fake_output.getvalue() == expected_output

    def test_comments_only_mode_flag(self):
        """Test comments-only mode flag in main."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write("""# This comment has color
variable = "String with color"
# Another comment with flavor
""")

        try:
            with (
                patch.object(sys, "argv", ["uwotm8", temp_path, "--comments-only"]),
                patch.object(sys, "stdout", StringIO()) as fake_output,
            ):
                exit_code = main()
                assert exit_code == 0
                assert "Reformatted" in fake_output.getvalue()

            # Verify that only comments were converted
            with open(temp_path) as f:
                content = f.read()
                assert "# This comment has colour" in content
                assert 'variable = "String with color"' in content
                assert "# Another comment with flavour" in content
        finally:
            os.unlink(temp_path)
