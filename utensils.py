"""Utensils (custom tool) definitions and implementations."""

import ast
import os
import subprocess

import os
import subprocess


def read_file(file_path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"
    except PermissionError:
        return f"Error: Permission denied reading file at '{file_path}'"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating it if necessary."""
    try:
        # Create directories if they don't exist
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to file '{file_path}'"
    except PermissionError:
        return f"Error: Permission denied writing to '{file_path}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def execute_command(command: str) -> str:
    """Execute a bash command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        return "\n".join(output) if output else "Command executed successfully with no output"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def edit_file(file_path: str, old_text: str, new_text: str) -> str:
    """
    Edit a file by replacing old_text with new_text.

    This is safer than write_file for modifications because it only changes
    the targeted text rather than rewriting the entire file.

    Args:
        file_path: Path to the file to edit
        old_text: The exact text to find and replace (must be unique in the file)
        new_text: The text to replace it with

    Returns:
        Success message or error description
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check that old_text exists in the file
        if old_text not in content:
            return f"Error: The specified old_text was not found in '{file_path}'. Make sure you're using the exact text including whitespace and indentation."

        # Check that old_text is unique
        count = content.count(old_text)
        if count > 1:
            return f"Error: The specified old_text appears {count} times in '{file_path}'. It must be unique. Include more surrounding context to make it unique."

        # Perform the replacement
        new_content = content.replace(old_text, new_text, 1)

        with open(file_path, 'w') as f:
            f.write(new_content)

        return f"Successfully edited '{file_path}'"
    except FileNotFoundError:
        return f"Error: File not found at path '{file_path}'"
    except PermissionError:
        return f"Error: Permission denied editing file at '{file_path}'"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def validate_python(code: str = None, file_path: str = None) -> str:
    """
    Validate Python code for syntax correctness.

    Can validate either provided code directly or read from a file.

    Args:
        code: Python code string to validate (optional)
        file_path: Path to a Python file to validate (optional)

    Returns:
        Success message if syntax is valid, error message with details if invalid
    """
    try:
        # Determine what to validate
        if code is not None and file_path is not None:
            return "Error: Provide either 'code' or 'file_path', not both"
        
        if code is None and file_path is None:
            return "Error: Must provide either 'code' or 'file_path' parameter"

        # Get the code to validate
        if file_path:
            if not file_path.endswith('.py'):
                return f"Warning: File '{file_path}' does not have .py extension. Validating anyway..."
            
            try:
                with open(file_path, 'r') as f:
                    code_to_validate = f.read()
                source_desc = f"file '{file_path}'"
            except FileNotFoundError:
                return f"Error: File not found at path '{file_path}'"
            except PermissionError:
                return f"Error: Permission denied reading file at '{file_path}'"
            except Exception as e:
                return f"Error reading file: {str(e)}"
        else:
            code_to_validate = code
            source_desc = "provided code"

        # Attempt to parse the code
        try:
            parsed = ast.parse(code_to_validate)
            
            # Count lines and AST nodes for proof of validation
            line_count = len(code_to_validate.splitlines())
            node_count = sum(1 for _ in ast.walk(parsed))
            
            # Generate detailed success output
            result = [
                "=" * 60,
                "✓ PYTHON SYNTAX VALIDATION SUCCESSFUL",
                "=" * 60,
                f"Source: {source_desc}",
                f"Lines of code: {line_count}",
                f"AST nodes parsed: {node_count}",
                f"Validation timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                "No syntax errors detected. Code is syntactically valid.",
                "=" * 60
            ]
            return "\n".join(result)
        except SyntaxError as e:
            error_details = [
                f"✗ Python syntax error in {source_desc}:",
                f"  Line {e.lineno}: {e.msg}",
            ]
            if e.text:
                error_details.append(f"  Code: {e.text.strip()}")
                if e.offset:
                    error_details.append(f"  {' ' * (e.offset + 7)}^")
            return "\n".join(error_details)
        except Exception as e:
            return f"Error parsing Python code: {str(e)}"

    except Exception as e:
        return f"Error validating Python: {str(e)}"


# Map utensil names to their implementation functions
UTENSIL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_command": execute_command,
    "edit_file": edit_file,
    "validate_python": validate_python,
}


def get_utensils_system_prompt() -> str:
    """
    Generate the system prompt that instructs Claude on how to use utensils.

    Returns:
        A formatted system prompt string describing the utensil format and available utensils
    """
    return """You are an agent that can use utensils (tools) to complete tasks. You MUST use utensils to interact with files and the system.

CRITICAL: When you need to read a file, write a file, or run a command, you MUST use a utensil. You cannot complete these tasks without using utensils.

Utensil Format (use EXACTLY this format):
UTENSIL:utensil_name
PARAM:param1=value1
PARAM:param2=value2
END_UTENSIL

For multi-line values (like file content), use BEGIN_VALUE and END_VALUE:
UTENSIL:write_file
PARAM:file_path=example.py
PARAM:content=BEGIN_VALUE
def hello():
    print("Hello, world!")

if __name__ == "__main__":
    hello()
END_VALUE
END_UTENSIL

Available utensils:
- read_file: Read file contents. Parameters: file_path
- write_file: Write to a file (use for NEW files only). Parameters: file_path, content (use BEGIN_VALUE/END_VALUE for multi-line content)
- edit_file: Edit an existing file by replacing text (PREFERRED for modifications). Parameters: file_path, old_text, new_text (use BEGIN_VALUE/END_VALUE for multi-line values)
- execute_command: Run a bash command. Parameters: command
- validate_python: Check if Python code is syntactically correct. Parameters: Either 'code' (string) OR 'file_path' (string), not both. Use BEGIN_VALUE/END_VALUE for multi-line code.

IMPORTANT: Do NOT use Anthropic's tool use format. Use ONLY the format shown above.
IMPORTANT: For multi-line content, you MUST use BEGIN_VALUE and END_VALUE.
IMPORTANT: When modifying existing files, ALWAYS use edit_file instead of write_file. This prevents accidental truncation or data loss.

Example - reading a file:
User asks: "read the file test.txt"
You respond:
I'll read that file for you.

UTENSIL:read_file
PARAM:file_path=test.txt
END_UTENSIL

Example - writing a NEW file:
User asks: "create a file called greeting.py with a function that prints hello"
You respond:
I'll create that file for you.

UTENSIL:write_file
PARAM:file_path=greeting.py
PARAM:content=BEGIN_VALUE
def greet():
    print("Hello!")

greet()
END_VALUE
END_UTENSIL

Example - editing an existing file:
User asks: "change the greet function to print 'Hello, World!' instead"
You respond:
I'll update the greet function.

UTENSIL:edit_file
PARAM:file_path=greeting.py
PARAM:old_text=print("Hello!")
PARAM:new_text=print("Hello, World!")
END_UTENSIL

def greet():
    try:
        print("Hello, World!")
    except Exception as e:
        print(f"Error: {e}")
END_VALUE
PARAM:new_text=BEGIN_VALUE
def greet():
    try:
        print("Hello, World!")
    except Exception as e:
        print(f"Error: {e}")
END_VALUE
END_UTENSIL

Then you'll receive the result and can respond with confirmation or analysis."""


def execute_utensil(name: str, params: dict) -> str:
    """
    Execute a utensil by name with the given parameters.

    Args:
        name: The name of the utensil to execute
        params: Dictionary of parameters to pass to the utensil

    Returns:
        The result of the utensil execution as a string
    """
    if name not in UTENSIL_FUNCTIONS:
        return f"Error: Unknown utensil '{name}'"

    try:
        utensil_func = UTENSIL_FUNCTIONS[name]
        return utensil_func(**params)
    except TypeError as e:
        return f"Error: Invalid arguments for utensil '{name}': {str(e)}"
    except Exception as e:
        return f"Error executing utensil '{name}': {str(e)}"