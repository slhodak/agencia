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

    print("\n✅ All tests passed!")
