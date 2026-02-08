"""Agent that accepts tasks from the command line or runs as an interactive REPL."""

import sys
import argparse
import logging
from dotenv import load_dotenv
from agent import Agent

# Import readline for better input handling with word navigation support
try:
    import readline
    # Enable tab completion and history
    readline.parse_and_bind('tab: complete')
    # Set up word navigation with Alt+Arrow keys (Meta keys)
    readline.parse_and_bind('"\e[1;3C": forward-word')  # Alt+Right
    readline.parse_and_bind('"\e[1;3D": backward-word')  # Alt+Left
    # Also support some common alternative sequences
    readline.parse_and_bind('"\e\e[C": forward-word')  # Alt+Right (alternative)
    readline.parse_and_bind('"\e\e[D": backward-word')  # Alt+Left (alternative)
    readline.parse_and_bind('"\ef": forward-word')  # Alt+f
    readline.parse_and_bind('"\eb": backward-word')  # Alt+b
except ImportError:
    # readline not available (e.g., on Windows)
    pass

# Load environment variables from .env file
load_dotenv()


def run_repl(debug=False):
    """Run the agent in interactive REPL mode."""
    # Set log level to DEBUG if debug flag is passed
    if debug:
        for name in ["agent", "streaming_parser"]:
            logger = logging.getLogger(name)
            for handler in logger.handlers:
                handler.setLevel(logging.DEBUG)

    # Initialize agent once for the entire session
    agent = Agent()
    
    # Display welcome message
    print("\n" + "="*60)
    print("🤖 Agent REPL - Interactive Mode")
    print("="*60)
    print("Enter your tasks and I'll help you complete them.")
    print("Type 'exit', 'quit', or press Ctrl+D to exit.")
    print("Press Ctrl+C to interrupt a running task.")
    print("="*60 + "\n")

    # REPL loop
    while True:
        try:
            # Display prompt and get user input
            user_input = input("Agent> ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!\n")
                break
            
            # Process the task through the agent
            try:
                agent.run_with_utensils(user_input)
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                # Keep the REPL running even if there's an error
                continue
                
        except EOFError:
            # Handle Ctrl+D
            print("\n\n👋 Goodbye!\n")
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\n\n⚠️  Interrupted. Type 'exit' or 'quit' to exit the REPL.\n")
            continue


def main():
    """Run the agent with a task from the command line or in REPL mode."""
    try:
        parser = argparse.ArgumentParser(
            description="Run the Python Coding Agent with a specified task or in interactive mode."
        )
        parser.add_argument(
            "task",
            nargs='?',  # Make task optional
            help="The task for the agent to perform (if not provided, enters REPL mode)"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )
        parser.add_argument(
            "--repl",
            action="store_true",
            help="Start in interactive REPL mode (ignores task argument)"
        )

        args = parser.parse_args()

        # If --repl flag is set or no task is provided, run in REPL mode
        if args.repl or args.task is None:
            run_repl(debug=args.debug)
        else:
            # Set log level to DEBUG if --debug flag is passed
            if args.debug:
                for name in ["agent", "streaming_parser"]:
                    logger = logging.getLogger(name)
                    for handler in logger.handlers:
                        handler.setLevel(logging.DEBUG)

            # Initialize and run the agent with the provided task
            agent = Agent()
            agent.run_with_utensils(args.task)
            
    except Exception as e:
        print(f"unknown error when calling api: {e}")


if __name__ == "__main__":
    main()