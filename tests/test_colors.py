"""Test script to demonstrate the color output."""

from colors import Colors

print("\n" + "="*60)
print("Color Test - REPL Enhancement")
print("="*60 + "\n")

print(f"{Colors.user('User:')} This is how user input looks")
print(f"{Colors.agent('🤖 Agent:')} This is how agent responses look")
print(f"{Colors.utensil('🔧 Utensil Call:')} {Colors.BOLD}read_file{Colors.RESET}")
print(f"{Colors.utensil('Parameters:')} {{'file_path': 'example.txt'}}")
print(f"{Colors.result('📤 Result of read_file:')}")
print(f"{Colors.DIM}File content here...{Colors.RESET}")
print(f"{Colors.error('❌ Error:')} This is how errors look")
print(f"{Colors.info('ℹ️  Info:')} This is how info messages look")
print(f"{Colors.header('Header Text')}")
print(f"{Colors.separator('='*60)}")

print("\n" + "Available color methods:")
print(f"  - {Colors.user('user()')}: Cyan for user input")
print(f"  - {Colors.agent('agent()')}: Green for agent responses")
print(f"  - {Colors.utensil('utensil()')}: Yellow for utensil calls")
print(f"  - {Colors.result('result()')}: Blue for results")
print(f"  - {Colors.error('error()')}: Red for errors")
print(f"  - {Colors.info('info()')}: Magenta for info")
print(f"  - {Colors.header('header()')}: Bold white for headers")
print(f"  - {Colors.separator('separator()')}: Dim gray for separators")

print("\n" + "="*60 + "\n")