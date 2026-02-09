"""Tests for Python syntax validation utensil."""

import pytest
from utensils import validate_python


def test_validate_valid_python_code():
    """Test validating syntactically correct Python code."""
    code = """
def hello():
    print("Hello, world!")
    return 42

if __name__ == "__main__":
    hello()
"""
    result = validate_python(code=code)
    assert "✓" in result
    assert "valid" in result.lower()


def test_validate_invalid_python_code():
    """Test validating syntactically incorrect Python code."""
    code = """
def hello(
    print("Missing closing parenthesis")
"""
    result = validate_python(code=code)
    assert "✗" in result or "error" in result.lower()
    assert "syntax" in result.lower()


def test_validate_simple_syntax_error():
    """Test detection of simple syntax errors."""
    code = "if True print('missing colon')"
    result = validate_python(code=code)
    assert "✗" in result or "error" in result.lower()


def test_validate_from_file(tmp_path):
    """Test validating Python code from a file."""
    # Create a valid Python file
    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def foo():\n    return 42\n")
    
    result = validate_python(file_path=str(valid_file))
    assert "✓" in result
    assert "valid" in result.lower()


def test_validate_invalid_file(tmp_path):
    """Test validating invalid Python code from a file."""
    # Create an invalid Python file
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def foo(\n    return 42\n")
    
    result = validate_python(file_path=str(invalid_file))
    assert "✗" in result or "error" in result.lower()


def test_validate_nonexistent_file():
    """Test validating a file that doesn't exist."""
    result = validate_python(file_path="/nonexistent/file.py")
    assert "error" in result.lower()
    assert "not found" in result.lower()


def test_validate_both_params_error():
    """Test that providing both code and file_path returns an error."""
    result = validate_python(code="print('hi')", file_path="test.py")
    assert "error" in result.lower()
    assert "both" in result.lower()


def test_validate_no_params_error():
    """Test that providing neither code nor file_path returns an error."""
    result = validate_python()
    assert "error" in result.lower()
    assert "must provide" in result.lower()


def test_validate_indentation_error():
    """Test detection of indentation errors."""
    code = """
def foo():
print("bad indentation")
"""
    result = validate_python(code=code)
    assert "✗" in result or "error" in result.lower()


def test_validate_non_py_extension(tmp_path):
    """Test validating a file without .py extension shows warning."""
    txt_file = tmp_path / "code.txt"
    txt_file.write_text("print('hello')")
    
    result = validate_python(file_path=str(txt_file))
    # Should still validate but may show warning
    assert "valid" in result.lower() or "warning" in result.lower()