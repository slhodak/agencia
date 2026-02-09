"""Example demonstrating the validate_python utensil."""

from utensils import validate_python

print("=" * 60)
print("Python Syntax Validation Examples")
print("=" * 60)

# Example 1: Valid Python code
print("\n1. Validating VALID Python code:")
print("-" * 40)
valid_code = """
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)
"""
print(f"Code:\n{valid_code}")
print(f"Result: {validate_python(code=valid_code)}")

# Example 2: Invalid Python code - missing colon
print("\n2. Validating INVALID Python code (missing colon):")
print("-" * 40)
invalid_code1 = """
def greet(name)
    return f"Hello, {name}!"
"""
print(f"Code:\n{invalid_code1}")
print(f"Result: {validate_python(code=invalid_code1)}")

# Example 3: Invalid Python code - mismatched parentheses
print("\n3. Validating INVALID Python code (mismatched parentheses):")
print("-" * 40)
invalid_code2 = """
def calculate(x, y):
    return (x + y
"""
print(f"Code:\n{invalid_code2}")
print(f"Result: {validate_python(code=invalid_code2)}")

# Example 4: Invalid Python code - bad indentation
print("\n4. Validating INVALID Python code (bad indentation):")
print("-" * 40)
invalid_code3 = """
def foo():
print("This should be indented")
"""
print(f"Code:\n{invalid_code3}")
print(f"Result: {validate_python(code=invalid_code3)}")

# Example 5: Validating from a file
print("\n5. Validating Python code from a file:")
print("-" * 40)
print(f"Validating 'utensils.py'...")
print(f"Result: {validate_python(file_path='utensils.py')}")

print("\n" + "=" * 60)