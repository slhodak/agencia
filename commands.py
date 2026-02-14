"""Command handling for the agent REPL."""

import logging
from typing import Optional, Tuple
from anthropic import Anthropic
import os

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles special commands that start with '/'."""

    def __init__(self, agent):
        """Initialize the command handler with a reference to the agent.

        Args:
            agent: The Agent instance to operate on
        """
        self.agent = agent
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def is_command(self, user_input: str) -> bool:
        """Check if the input is a command (starts with '/').

        Args:
            user_input: The user's input string

        Returns:
            True if input starts with '/', False otherwise
        """
        return user_input.strip().startswith('/')

    def parse_command(self, user_input: str) -> Tuple[str, list]:
        """Parse a command into command name and arguments.

        Args:
            user_input: The command string (including leading '/')

        Returns:
            Tuple of (command_name, arguments_list)
        """
        # Remove leading '/' and split into parts
        parts = user_input.strip()[1:].split()
        command_name = parts[0].lower() if parts else ""
        arguments = parts[1:] if len(parts) > 1 else []

        return command_name, arguments

    def execute_command(self, user_input: str) -> bool:
        """Execute a command and return whether it was handled.

        Args:
            user_input: The command string

        Returns:
            True if command was recognized and executed, False otherwise
        """
        command_name, arguments = self.parse_command(user_input)

        if command_name == "compact":
            return self._handle_compact()
        elif command_name == "clear":
            return self._handle_clear()
        elif command_name == "help":
            return self._handle_help()
        elif command_name == "models":
            return self._handle_models()
        elif command_name == "model":
            return self._handle_model(arguments)
        else:
            print(f"\n❌ Unknown command: /{command_name}")
            print("Type /help to see available commands.\n")
            return False

    def _handle_compact(self) -> bool:
        """Compact the conversation history by creating a summary.

        Returns:
            True if successful
        """
        if not self.agent.message_history:
            print("\n💡 No conversation history to compact.\n")
            return True

        print("\n🔄 Compacting conversation history...")

        # Build a prompt to summarize the conversation
        conversation_text = self._format_history_for_summary()

        summary_prompt = f"""Please provide a succinct summary of the following conversation history.
The summary should preserve key context, decisions made, and important information, but be much shorter than the original.
Focus on what's essential for continuing the conversation effectively.

Conversation history:
{conversation_text}

Please respond with ONLY the summary, no preamble or explanation."""

        try:
            # Call Claude to generate summary
            response = self.client.messages.create(
                model=self.agent.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ]
            )

            summary = response.content[0].text

            # Replace conversation history with summary
            self.agent.message_history = [
                {
                    "role": "user",
                    "content": f"[Previous conversation summary]: {summary}"
                }
            ]

            print(f"\n✅ Conversation compacted. Summary:\n")
            print(f"{summary}\n")

            return True

        except Exception as e:
            print(f"\n❌ Error compacting conversation: {e}\n")
            return False

    def _handle_clear(self) -> bool:
        """Clear the conversation history.

        Returns:
            True if successful
        """
        self.agent.reset()
        print("\n✅ Conversation history cleared. Starting fresh!\n")
        return True

    def _handle_help(self) -> bool:
        """Display help information about available commands.

        Returns:
            True
        """
        print("\n" + "="*60)
        print("📋 Available Commands")
        print("="*60)
        print("/compact  - Summarize conversation history to save tokens")
        print("/clear    - Erase conversation history and start fresh")
        print("/models   - List available models")
        print("/model    - Show or switch the current model")
        print("/help     - Display this help message")
        print("="*60 + "\n")
        return True

    def _handle_models(self) -> bool:
        """List available models."""
        models = self.agent.model_manager.list_available_models()
        current = self.agent.model
        print("\n" + "="*60)
        print("📋 Available Models")
        print("="*60)
        for model_id, info in models.items():
            marker = " ← current" if model_id == current else ""
            print(f"  {model_id}")
            print(f"    {info['display_name']} - {info['description']}{marker}")
        print("="*60)
        print("Use /model <id> to switch.\n")
        return True

    def _handle_model(self, arguments: list) -> bool:
        """Switch to a specified model."""
        if not arguments:
            print(f"\n📋 Current model: {self.agent.model}")
            print("Use /model <id> to switch or /models to list available models.\n")
            return True

        new_model = arguments[0]
        if self.agent.switch_model(new_model):
            print(f"\n✅ Switched to {new_model}\n")
        else:
            print(f"\n❌ Unknown model: {new_model}")
            print("Use /models to see available models.\n")
        return True

    def _format_history_for_summary(self) -> str:
        """Format the message history as readable text for summarization.

        Returns:
            Formatted conversation string
        """
        formatted = []
        for msg in self.agent.message_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted.append(f"{role}: {content}\n")

        return "\n".join(formatted)
