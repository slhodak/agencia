"""Streaming parser for utensil calls in Claude's token stream."""

import logging
from enum import Enum
from typing import Optional

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Allow all levels, let handler decide

# Only add handler if none exist (avoid duplicate handlers on reimport)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)  # Default to INFO level
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ParserState(Enum):
    """States for the utensil call parser state machine."""
    NORMAL = "normal"  # Accumulating regular text
    IN_UTENSIL = "in_utensil"  # Inside a utensil call, accumulating parameters
    IN_MULTILINE_VALUE = "in_multiline_value"  # Accumulating multi-line parameter value
    COMPLETE = "complete"  # A complete utensil call has been parsed


class StreamingUtensilParser:
    """
    A state machine parser that processes tokens as they arrive from the streaming API.

    This parser detects utensil calls in the format:
    UTENSIL:utensil_name
    PARAM:param1=value1
    PARAM:param2=BEGIN_VALUE
    line 1
    line 2
    END_VALUE
    END_UTENSIL

    Single-line parameters use: PARAM:key=value
    Multi-line parameters use: PARAM:key=BEGIN_VALUE ... END_VALUE
    """

    def __init__(self):
        """Initialize the parser in NORMAL state."""
        self.state = ParserState.NORMAL
        self.text_buffer = ""  # Accumulates regular text (non-utensil)
        self.token_buffer = ""  # Accumulates tokens to form complete lines
        self.utensil_name = None
        self.utensil_params = {}
        # The raw text of the utensil call (for message history)
        self.utensil_text = ""
        # For multi-line value accumulation
        self.multiline_key = None
        self.multiline_lines = []

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
            line: A complete line of text (note: we preserve original for multi-line values)
        """
        # For multi-line values, we need to preserve the original line (with whitespace)
        original_line = line
        line = line.strip()
        logger.debug(f"Processing line: {repr(line)}, State: {self.state}")

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
                    key = key.strip()
                    value = value.strip()

                    # Check if this is a multi-line value
                    if value == "BEGIN_VALUE":
                        self.state = ParserState.IN_MULTILINE_VALUE
                        self.multiline_key = key
                        self.multiline_lines = []
                        logger.debug(f"Starting multi-line value for key: {key}")
                    else:
                        self.utensil_params[key] = value

            # Check for end marker
            elif line == "END_UTENSIL":
                self.state = ParserState.COMPLETE
                logger.debug("Transitioned to COMPLETE state")

            # Any other line in utensil context is ignored (or could be an error)

        elif self.state == ParserState.IN_MULTILINE_VALUE:
            self.utensil_text += original_line + "\n"

            # Check for end of multi-line value
            if line == "END_VALUE":
                # Join accumulated lines and store as parameter
                self.utensil_params[self.multiline_key] = "\n".join(self.multiline_lines)
                logger.debug(f"Completed multi-line value for key: {self.multiline_key}")
                self.multiline_key = None
                self.multiline_lines = []
                self.state = ParserState.IN_UTENSIL
            else:
                # Accumulate this line (preserve original whitespace for code)
                self.multiline_lines.append(original_line)

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
        self.multiline_key = None
        self.multiline_lines = []

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
