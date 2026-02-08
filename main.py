"""Agent that accepts tasks from the command line."""

import sys
import argparse
import logging
from dotenv import load_dotenv
from agent import Agent

# Load environment variables from .env file
load_dotenv()


def main():
    try:
        """Run the agent with a task from the command line."""
        parser = argparse.ArgumentParser(
            description="Run the Python Coding Agent with a specified task."
        )
        parser.add_argument(
            "task",
            help="The task for the agent to perform"
        )
        parser.add_argument(
            "--utensils",
            action="store_true",
            help="Use custom utensils format instead of Anthropic's built-in tools"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )

        args = parser.parse_args()

        # Set log level to DEBUG if --debug flag is passed
        if args.debug:
            for name in ["agent", "streaming_parser"]:
                logger = logging.getLogger(name)
                for handler in logger.handlers:
                    handler.setLevel(logging.DEBUG)

        # Initialize and run the agent with the provided task
        agent = Agent()
        if args.utensils:
            agent.run_with_utensils(args.task)
        else:
            agent.run(args.task)
    except Exception as e:
        print(f"unknown error when calling api: {e}")


if __name__ == "__main__":
    main()
