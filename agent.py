"""Main agent loop with Claude API integration."""

import logging
import os
from anthropic import Anthropic
from utensils import get_utensils_system_prompt, execute_utensil
from streaming_parser import StreamingUtensilParser

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class Agent:
    def __init__(self):
        """Initialize the agent with an Anthropic client."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.message_history = []
        self.model = "claude-sonnet-4-5-20250929"

    def run_with_utensils(self, user_prompt: str) -> str:
        """
        Run the agent with custom utensils format using streaming API.

        This method demonstrates how LLM tool calling works under the hood by
        parsing custom tool call syntax from the streaming token output.

        Args:
            user_prompt: The task for the agent to complete

        Returns:
            The final response from Claude
        """
        # Build system prompt with utensil instructions
        system_prompt = get_utensils_system_prompt()

        # Initialize conversation with user prompt
        self.message_history = [
            {"role": "user", "content": user_prompt}
        ]

        print(f"\n{'='*60}")
        print(f"User: {user_prompt}")
        print(f"{'='*60}\n")

        # Agentic loop
        while True:
            # Create streaming request
            with self.client.messages.stream(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=self.message_history
            ) as stream:
                # Initialize parser for this stream
                parser = StreamingUtensilParser()

                # Process tokens as they arrive
                for token in stream.text_stream:
                    parser.add_token(token)

                    # Check if we have a complete utensil call mid-stream
                    if parser.has_utensil_call():
                        break

            # Finalize parser to process any remaining tokens (handles END_UTENSIL without trailing newline)
            parser.finalize()

            # Check if there's a utensil call to execute (detected mid-stream or after finalize)
            if parser.has_utensil_call():
                logger.debug("Utensil detected!")
                # Extract the utensil call
                utensil_call = parser.get_utensil_call()
                utensil_name = utensil_call["name"]
                utensil_params = utensil_call["params"]
                utensil_text = utensil_call["text"]

                print(f"Utensil Call: {utensil_name}")
                print(f"Parameters: {utensil_params}")

                # Execute the utensil
                result = execute_utensil(utensil_name, utensil_params)

                # Add assistant message with the utensil call to history
                assistant_text = parser.get_text()
                if assistant_text:
                    full_response = assistant_text + "\n\n" + utensil_text
                else:
                    full_response = utensil_text

                self.message_history.append({
                    "role": "assistant",
                    "content": full_response
                })

                # Add user message with the result
                self.message_history.append({
                    "role": "user",
                    "content": result
                })

                # Continue the agentic loop
                continue

            # No utensil call - agent is done
            final_response = parser.get_text()

            if final_response:
                print(f"\nAgent: {final_response}\n")

            return final_response

    def reset(self):
        """Clear the message history for a new conversation."""
        self.message_history = []