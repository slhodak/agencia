"""
Simple test script to verify REPL implementation.
This script tests the basic functionality without requiring actual user input.
"""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from agent import Agent


def test_agent_initialization():
    """Test that agent can be initialized."""
    print("Testing agent initialization...")
    try:
        agent = Agent()
        print("✓ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        return False


def test_agent_has_required_methods():
    """Test that agent has required methods."""
    print("\nTesting agent methods...")
    try:
        agent = Agent()
        assert hasattr(agent, 'run_with_utensils'), "Missing run_with_utensils method"
        assert hasattr(agent, 'reset'), "Missing reset method"
        assert hasattr(agent, 'message_history'), "Missing message_history attribute"
        print("✓ Agent has all required methods and attributes")
        return True
    except AssertionError as e:
        print(f"✗ Agent missing required component: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking agent methods: {e}")
        return False


def test_message_history_persistence():
    """Test that message history is maintained."""
    print("\nTesting message history persistence...")
    try:
        agent = Agent()
        initial_length = len(agent.message_history)
        print(f"  Initial history length: {initial_length}")
        
        # Message history should start empty
        assert initial_length == 0, "Message history should start empty"
        
        print("✓ Message history initialized correctly")
        return True
    except AssertionError as e:
        print(f"✗ Message history test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing message history: {e}")
        return False


def test_agent_reset():
    """Test that agent reset clears history."""
    print("\nTesting agent reset...")
    try:
        agent = Agent()
        
        # Manually add a message to history
        agent.message_history.append({"role": "user", "content": "test"})
        assert len(agent.message_history) == 1, "History should have one message"
        
        # Reset should clear history
        agent.reset()
        assert len(agent.message_history) == 0, "History should be empty after reset"
        
        print("✓ Agent reset works correctly")
        return True
    except AssertionError as e:
        print(f"✗ Reset test failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing reset: {e}")
        return False


def test_main_imports():
    """Test that main.py imports work."""
    print("\nTesting main.py imports...")
    try:
        import main
        assert hasattr(main, 'run_repl'), "Missing run_repl function"
        assert hasattr(main, 'main'), "Missing main function"
        print("✓ main.py imports and functions exist")
        return True
    except ImportError as e:
        print(f"✗ Failed to import main.py: {e}")
        return False
    except AssertionError as e:
        print(f"✗ main.py missing required function: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing main.py: {e}")
        return False


def test_utensils_import():
    """Test that utensils can be imported."""
    print("\nTesting utensils imports...")
    try:
        from utensils import get_utensils_system_prompt, execute_utensil, UTENSIL_FUNCTIONS
        
        # Check system prompt is not empty
        prompt = get_utensils_system_prompt()
        assert len(prompt) > 0, "System prompt should not be empty"
        
        # Check utensil functions are defined
        assert len(UTENSIL_FUNCTIONS) > 0, "Should have utensil functions defined"
        assert 'read_file' in UTENSIL_FUNCTIONS, "Missing read_file utensil"
        assert 'write_file' in UTENSIL_FUNCTIONS, "Missing write_file utensil"
        assert 'execute_command' in UTENSIL_FUNCTIONS, "Missing execute_command utensil"
        
        print("✓ Utensils imported and configured correctly")
        return True
    except ImportError as e:
        print(f"✗ Failed to import utensils: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Utensils configuration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing utensils: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("="*60)
    print("REPL Implementation Test Suite")
    print("="*60)
    
    tests = [
        test_agent_initialization,
        test_agent_has_required_methods,
        test_message_history_persistence,
        test_agent_reset,
        test_main_imports,
        test_utensils_import,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! REPL is ready to use.")
        print("\nTo start the REPL, run: python main.py")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())