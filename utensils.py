"""Utensils (custom tool) definitions and implementations."""

from tools import read_file, write_file, execute_command


# Map utensil names to their implementation functions
UTENSIL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_command": execute_command,
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
- write_file: Write to a file. Parameters: file_path, content (use BEGIN_VALUE/END_VALUE for multi-line content)
- execute_command: Run a bash command. Parameters: command

IMPORTANT: Do NOT use Anthropic's tool use format. Use ONLY the format shown above.
IMPORTANT: For write_file with multi-line content, you MUST use BEGIN_VALUE and END_VALUE.

Example - reading a file:
User asks: "read the file test.txt"
You respond:
I'll read that file for you.

UTENSIL:read_file
PARAM:file_path=test.txt
END_UTENSIL

Example - writing a file:
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
