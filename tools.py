"""Tool definitions and implementations for the agent."""

import os
import subprocess


# Tool Definitions - used for Claude API
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the specified path",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file at the specified path. Creates the file if it doesn't exist, overwrites if it does.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "execute_command",
        "description": "Execute a bash command and return its output. Runs in the current working directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    }
]


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


# Tool dispatcher - maps tool names to functions
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_command": execute_command,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name with the given input parameters."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        tool_func = TOOL_FUNCTIONS[tool_name]
        return tool_func(**tool_input)
    except TypeError as e:
        return f"Error: Invalid arguments for tool '{tool_name}': {str(e)}"
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
