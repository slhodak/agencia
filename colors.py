"""ANSI color codes for terminal output."""

class Colors:
    """ANSI color codes for terminal styling."""
    
    # Reset
    RESET = '\033[0m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright text colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Wrap text in color codes."""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def user(text: str) -> str:
        """Format user input."""
        return Colors.colorize(text, Colors.BRIGHT_CYAN)
    
    @staticmethod
    def agent(text: str) -> str:
        """Format agent response."""
        return Colors.colorize(text, Colors.BRIGHT_GREEN)
    
    @staticmethod
    def utensil(text: str) -> str:
        """Format utensil call."""
        return Colors.colorize(text, Colors.BRIGHT_YELLOW)
    
    @staticmethod
    def result(text: str) -> str:
        """Format utensil result."""
        return Colors.colorize(text, Colors.BRIGHT_BLUE)
    
    @staticmethod
    def error(text: str) -> str:
        """Format error message."""
        return Colors.colorize(text, Colors.BRIGHT_RED)
    
    @staticmethod
    def info(text: str) -> str:
        """Format info message."""
        return Colors.colorize(text, Colors.BRIGHT_MAGENTA)
    
    @staticmethod
    def separator(text: str) -> str:
        """Format separator."""
        return Colors.colorize(text, Colors.DIM + Colors.BRIGHT_BLACK)
    
    @staticmethod
    def header(text: str) -> str:
        """Format header."""
        return Colors.colorize(text, Colors.BOLD + Colors.BRIGHT_WHITE)