# Agent Python Validation Demo

This document shows how an agent would use the `validate_python` utensil to check Python syntax.

## Example 1: Validating code before writing to file

**User:** "Create a Python script that calculates fibonacci numbers, but first validate the syntax"

**Agent:** I'll create the fibonacci calculator and validate its syntax first.

```
UTENSIL:validate_python
PARAM:code=BEGIN_VALUE
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")