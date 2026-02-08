"""Streaming parser for utensil calls in Claude's token stream."""

from enum import Enum
from typing import Optional


class ParserState(Enum):
    """States for the utensil call parser state machine."""
    NORMAL = "normal"  # Accumulating regular text
    IN_UTENSIL = "in_utensil"  # Inside a utensil call, accumulating parameters
    COMPLETE = "complete"  # A complete utensil call has been parsed


class StreamingUtensilParser:
    """
    A state machine parser that processes tokens as they arrive from the streaming API.

    This parser detects utensil calls in the format:
    UTENSIL:utensil_name
    PARAM:param1=value1
    PARAM:param2=value2
    END_UTENSIL
    """

    def __init__(self):
        """Initialize the parser in NORMAL state."""
        self.state = ParserState.NORMAL
        self.text_buffer = ""  # Accumulates regular text (non-utensil)
        self.token_buffer = ""  # Accumulates tokens to form complete lines
        self.utensil_name = None
        self.utensil_params = {}
        self.utensil_text = ""  # The raw text of the utensil call (for message history)

    def add_token(self, token: str):
        """
        Add a new token from the stream and update parser state.

        Args:
            token: A single token from the streaming API
        """
        self.token_buffer += token

        # Process complete lines
        while "\n" in self.token_buffer:
            line, self.token_buffer = self.token_buffer.split("\n", 1)
            self._process_line(line)

    def _process_line(self, line: str):
        """
        Process a complete line and update state accordingly.

        Args:
            line: A complete line of text
        """
        line = line.strip()
        print(f"\n[PARSER] Processing line: {repr(line)}, State: {self.state}")  # Debug

        if self.state == ParserState.NORMAL:
            # Check if this line starts a utensil call
            if line.startswith("UTENSIL:"):
                self.state = ParserState.IN_UTENSIL
                self.utensil_name = line[len("UTENSIL:"):].strip()
                self.utensil_params = {}
                self.utensil_text = line + "\n"
            else:
                # Regular text
                self.text_buffer += line + "\n"

        elif self.state == ParserState.IN_UTENSIL:
            self.utensil_text += line + "\n"

            # Check for parameter line
            if line.startswith("PARAM:"):
                param_line = line[len("PARAM:"):].strip()
                # Split on first '=' to handle values with '=' in them
                if "=" in param_line:
                    key, value = param_line.split("=", 1)
                    self.utensil_params[key.strip()] = value.strip()

            # Check for end marker
            elif line == "END_UTENSIL":
                self.state = ParserState.COMPLETE
                print(f"[PARSER] Transitioned to COMPLETE state")  # Debug

            # Any other line in utensil context is ignored (or could be an error)

    def has_utensil_call(self) -> bool:
        """
        Check if a complete utensil call has been parsed.

        Returns:
            True if a complete utensil is ready to execute
        """
        return self.state == ParserState.COMPLETE

    def get_utensil_call(self) -> Optional[dict]:
        """
        Extract the complete utensil call and reset state for next call.

        Returns:
            Dictionary with 'name', 'params', and 'text' keys, or None if no complete call
        """
        if not self.has_utensil_call():
            return None

        result = {
            "name": self.utensil_name,
            "params": self.utensil_params,
            "text": self.utensil_text.strip()
        }

        # Reset utensil-specific state to parse next call
        self.state = ParserState.NORMAL
        self.utensil_name = None
        self.utensil_params = {}
        self.utensil_text = ""

        return result

    def get_text(self) -> str:
        """
        Get accumulated non-utensil text.

        Returns:
            The text buffer containing regular agent responses
        """
        return self.text_buffer.strip()

    def finalize(self):
        """
        Finalize parsing by processing any remaining tokens in the buffer.
        Call this when the stream ends.
        """
        # Process any remaining content in token_buffer as a final line
        if self.token_buffer.strip():
            self._process_line(self.token_buffer)
            self.token_buffer = ""
