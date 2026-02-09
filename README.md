# Agent with Interactive REPL

Hi, human author here. This is a learning project to get familiar with agents from the inside. It implements a custom tooling framework ("utensils"), and uses a custom streaming parser to detect and execute utensil calls, while explicitly instructing Claude not to use its own native tool call format.

Now back to our ai-generated introduction...


An intelligent agent powered by Claude that can read files, write files, and execute commands through an interactive REPL interface.

## Features

- 🔄 **Interactive REPL Mode**: Continuous interaction without restarting
- 🛠️ **Utensils (Tools)**: Read/write files and execute bash commands
- 💬 **Conversation History**: Maintains context within a session
- 🎯 **Single-Task Mode**: Run one-off tasks from command line
- 🐛 **Debug Mode**: Detailed logging for troubleshooting
- ⚡ **Streaming Responses**: Real-time output as agent thinks

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Anthropic API key:
```bash
# Create a .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Usage

#### Interactive REPL Mode (Recommended)

Start the REPL by running without arguments:
```bash
python main.py
```

You'll see:
```
============================================================
🤖 Agent REPL - Interactive Mode
============================================================
Enter your tasks and I'll help you complete them.
Type 'exit', 'quit', or press Ctrl+D to exit.
Press Ctrl+C to interrupt a running task.
============================================================

Agent> 
```

Now you can interact continuously:
```
Agent> create a file called hello.py with a hello world script
[Agent creates the file]

Agent> read the file hello.py
[Agent reads and displays the content]

Agent> run the hello.py script
[Agent executes the script]

Agent> exit
👋 Goodbye!
```

#### Single-Task Mode

Run a single task and exit:
```bash
python main.py "create a python script that prints hello world"
```

#### Debug Mode

Enable detailed logging:
```bash
python main.py --debug
```

## Available Utensils (Tools)

The agent can use these utensils to interact with your system:

### read_file
Read contents of a file
```
Agent> read the file example.txt
```

### write_file
Create or overwrite a file
```
Agent> create a file called test.py with a function that adds two numbers
```

### execute_command
Run bash commands
```
Agent> list all python files in the current directory
Agent> run the tests with pytest
```

## Examples

### File Operations
```
Agent> create a todo list file with 3 items
Agent> read todo.txt
Agent> add another item to the todo list
```

### Code Development
```
Agent> create a calculator script in Python
Agent> test the calculator with some examples
Agent> add error handling to the calculator
```

### System Commands
```
Agent> show me the current directory structure
Agent> find all .py files
Agent> check the git status
```

## Tips

- **Context Awareness**: The agent remembers previous interactions in the same session
- **Natural Language**: Describe what you want in plain English
- **Iterative Development**: Build complex tasks step by step
- **Ctrl+C**: Interrupt a running task without exiting the REPL
- **exit/quit**: Exit the REPL when done

## Architecture

### Components

- **main.py**: Entry point with REPL loop
- **agent.py**: Core agent logic with Claude API integration
- **utensils.py**: Custom tool definitions, implementations, and execution
- **streaming_parser.py**: Real-time parsing of tool calls from streaming responses

### How It Works

1. User enters a task in the REPL
2. Agent receives task with system prompt explaining available utensils
3. Claude streams response tokens in real-time
4. Parser detects utensil calls in the streaming output
5. Utensils are executed and results fed back to Claude
6. Agent continues until task is complete
7. REPL returns to prompt for next task

## Error Handling

- **Invalid Commands**: Agent provides helpful error messages
- **File Not Found**: Clear feedback when files don't exist
- **Command Failures**: Bash errors are captured and displayed
- **API Errors**: Graceful handling with option to retry
- **Interrupts**: Ctrl+C stops current task but keeps REPL running

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Your Claude API key (required)

### Model

The agent uses `claude-sonnet-4-5-20250929` by default. You can modify this in `agent.py`.

## Development

### Running Tests

The project follows Python best practices with tests in a dedicated `tests/` directory.

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_streaming_parser.py
```

Run with coverage report:
```bash
pytest --cov=. --cov-report=html
```

Run the color demonstration (not a unit test):
```bash
python tests/test_colors.py
```

### Test Structure
- `tests/test_streaming_parser.py` - Unit tests for streaming parser
- `tests/test_repl.py` - Integration tests for REPL functionality
- `tests/test_colors.py` - Visual demonstration of color output
- `tests/conftest.py` - Shared pytest configuration and fixtures
- `pytest.ini` - Pytest configuration

### Debug Mode
```bash
python main.py --debug
```

This enables detailed logging of:
- Token streaming
- Utensil detection
- Parameter parsing
- API interactions

## Limitations

- Single-threaded execution (one task at a time)
- No persistent memory across sessions
- Relies on terminal for command history
- No multi-line input support

## Future Enhancements

Potential features for future versions:
- Session save/restore
- Multi-line input mode
- Custom utensil plugins
- Configuration file support
- Token usage tracking
- Colored output


---

**Need Help?** Start the REPL with `python main.py` and ask the agent! It's self-documenting.