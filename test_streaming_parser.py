"""Unit tests for the streaming parser."""

from streaming_parser import StreamingUtensilParser, ParserState


def test_simple_utensil_call():
    """Test parsing a simple utensil call with newlines."""
    parser = StreamingUtensilParser()

    # Simulate streaming tokens
    tokens = "UTENSIL:read_file\nPARAM:file_path=test.txt\nEND_UTENSIL\n"
    for token in tokens:
        parser.add_token(token)

    assert parser.has_utensil_call(), "Should detect complete utensil call"

    call = parser.get_utensil_call()
    assert call["name"] == "read_file"
    assert call["params"]["file_path"] == "test.txt"
    print("✓ test_simple_utensil_call passed")


def test_utensil_with_text_before():
    """Test utensil call with regular text before it."""
    parser = StreamingUtensilParser()

    tokens = "I'll read the file.\n\nUTENSIL:read_file\nPARAM:file_path=test.txt\nEND_UTENSIL\n"
    for token in tokens:
        parser.add_token(token)

    assert parser.has_utensil_call(), "Should detect utensil call"

    call = parser.get_utensil_call()
    assert call["name"] == "read_file"

    text = parser.get_text()
    assert "I'll read the file." in text
    print("✓ test_utensil_with_text_before passed")


def test_no_trailing_newline():
    """Test utensil call without trailing newline after END_UTENSIL."""
    parser = StreamingUtensilParser()

    # No newline after END_UTENSIL - this might be the issue!
    tokens = "UTENSIL:read_file\nPARAM:file_path=test.txt\nEND_UTENSIL"
    for token in tokens:
        parser.add_token(token)

    # Need to finalize to process the last line without newline
    parser.finalize()

    assert parser.has_utensil_call(), "Should detect utensil call after finalize"

    call = parser.get_utensil_call()
    assert call["name"] == "read_file"
    print("✓ test_no_trailing_newline passed")


def test_multiple_params():
    """Test utensil with multiple parameters."""
    parser = StreamingUtensilParser()

    tokens = "UTENSIL:write_file\nPARAM:file_path=test.txt\nPARAM:content=Hello World\nEND_UTENSIL\n"
    for token in tokens:
        parser.add_token(token)

    assert parser.has_utensil_call()

    call = parser.get_utensil_call()
    assert call["name"] == "write_file"
    assert call["params"]["file_path"] == "test.txt"
    assert call["params"]["content"] == "Hello World"
    print("✓ test_multiple_params passed")


def test_param_with_equals_in_value():
    """Test parameter value containing '=' character."""
    parser = StreamingUtensilParser()

    tokens = "UTENSIL:execute_command\nPARAM:command=echo x=5\nEND_UTENSIL\n"
    for token in tokens:
        parser.add_token(token)

    assert parser.has_utensil_call()

    call = parser.get_utensil_call()
    assert call["params"]["command"] == "echo x=5", "Should split on first '=' only"
    print("✓ test_param_with_equals_in_value passed")


def test_token_by_token_streaming():
    """Test realistic token-by-token streaming."""
    parser = StreamingUtensilParser()

    # Simulate tokens arriving one at a time (more realistic)
    message = "I'll help you.\n\nUTENSIL:read_file\nPARAM:file_path=/path/to/file.txt\nEND_UTENSIL\n"

    for char in message:
        parser.add_token(char)
        # Check after each character
        if parser.has_utensil_call():
            break

    assert parser.has_utensil_call(), "Should eventually detect utensil"

    call = parser.get_utensil_call()
    assert call["name"] == "read_file"
    assert call["params"]["file_path"] == "/path/to/file.txt"
    print("✓ test_token_by_token_streaming passed")


def test_incomplete_utensil():
    """Test that incomplete utensil is not detected."""
    parser = StreamingUtensilParser()

    tokens = "UTENSIL:read_file\nPARAM:file_path=test.txt\n"
    for token in tokens:
        parser.add_token(token)

    assert not parser.has_utensil_call(), "Should not detect incomplete utensil"
    assert parser.state == ParserState.IN_UTENSIL, "Should be in IN_UTENSIL state"
    print("✓ test_incomplete_utensil passed")


def test_text_with_utensil_keyword():
    """Test that 'UTENSIL:' in regular text doesn't trigger false positive."""
    parser = StreamingUtensilParser()

    # This should NOT be detected as a utensil (not at start of line)
    tokens = "The word UTENSIL: appears in this text\n"
    for token in tokens:
        parser.add_token(token)

    assert not parser.has_utensil_call()
    assert parser.state == ParserState.NORMAL

    text = parser.get_text()
    assert "UTENSIL:" in text
    print("✓ test_text_with_utensil_keyword passed")


def test_multiple_utensil_calls_in_one_response():
    """Test parsing multiple utensil calls in a single response."""
    parser = StreamingUtensilParser()

    tokens = """I'll read both files for you.

UTENSIL:read_file
PARAM:file_path=file1.txt
END_UTENSIL

Now let me read the second one.

UTENSIL:read_file
PARAM:file_path=file2.txt
END_UTENSIL

And now I'll write a summary.

UTENSIL:write_file
PARAM:file_path=summary.txt
PARAM:content=Summary here
END_UTENSIL
"""
    for token in tokens:
        parser.add_token(token)

    assert parser.utensil_count() == 3, f"Should have 3 utensil calls, got {parser.utensil_count()}"

    calls = parser.get_all_utensil_calls()
    assert len(calls) == 3
    assert calls[0]["name"] == "read_file"
    assert calls[0]["params"]["file_path"] == "file1.txt"
    assert calls[1]["name"] == "read_file"
    assert calls[1]["params"]["file_path"] == "file2.txt"
    assert calls[2]["name"] == "write_file"
    assert calls[2]["params"]["file_path"] == "summary.txt"

    # Queue should be empty after get_all_utensil_calls
    assert parser.utensil_count() == 0
    print("✓ test_multiple_utensil_calls_in_one_response passed")


def test_text_between_and_after_utensils():
    """Test that text between and after utensil calls is captured."""
    parser = StreamingUtensilParser()

    tokens = """First I'll read the file.

UTENSIL:read_file
PARAM:file_path=test.txt
END_UTENSIL

Now based on the contents, let me update it.

UTENSIL:write_file
PARAM:file_path=test.txt
PARAM:content=Updated
END_UTENSIL

All done! The file has been updated successfully.
"""
    for token in tokens:
        parser.add_token(token)

    assert parser.utensil_count() == 2

    text = parser.get_text()
    assert "First I'll read the file." in text
    assert "Now based on the contents" in text
    assert "All done!" in text
    print("✓ test_text_between_and_after_utensils passed")


def test_get_utensil_call_pops_from_queue():
    """Test that get_utensil_call returns calls one at a time."""
    parser = StreamingUtensilParser()

    tokens = """UTENSIL:read_file
PARAM:file_path=a.txt
END_UTENSIL

UTENSIL:read_file
PARAM:file_path=b.txt
END_UTENSIL
"""
    for token in tokens:
        parser.add_token(token)

    assert parser.utensil_count() == 2

    call1 = parser.get_utensil_call()
    assert call1["params"]["file_path"] == "a.txt"
    assert parser.utensil_count() == 1

    call2 = parser.get_utensil_call()
    assert call2["params"]["file_path"] == "b.txt"
    assert parser.utensil_count() == 0

    call3 = parser.get_utensil_call()
    assert call3 is None
    print("✓ test_get_utensil_call_pops_from_queue passed")


if __name__ == "__main__":
    print("Running streaming parser tests...\n")

    test_simple_utensil_call()
    test_utensil_with_text_before()
    test_no_trailing_newline()
    test_multiple_params()
    test_param_with_equals_in_value()
    test_token_by_token_streaming()
    test_incomplete_utensil()
    test_text_with_utensil_keyword()
    test_multiple_utensil_calls_in_one_response()
    test_text_between_and_after_utensils()
    test_get_utensil_call_pops_from_queue()

    print("\n✅ All tests passed!")
