"""
Calculator Script

Performs basic mathematical operations.
Usage: python calculator.py [operation] [num1] [num2]
Operations: add, subtract, multiply, divide
"""

import sys

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def main():
    if len(sys.argv) < 4:
        print("Calculator - Basic Mathematical Operations")
        print("=" * 50)
        print()
        print("Usage: python calculator.py [operation] [num1] [num2]")
        print()
        print("Available operations:")
        print("  add        - Add two numbers")
        print("  subtract   - Subtract second from first")
        print("  multiply   - Multiply two numbers")
        print("  divide     - Divide first by second")
        print()
        print("Example: python calculator.py add 5 3")
        print()
        return
    
    operation = sys.argv[1].lower()
    
    try:
        num1 = float(sys.argv[2])
        num2 = float(sys.argv[3])
    except ValueError:
        print("Error: Please provide valid numbers")
        return
    
    operations = {
        'add': add,
        'subtract': subtract,
        'multiply': multiply,
        'divide': divide
    }
    
    if operation not in operations:
        print(f"Error: Unknown operation '{operation}'")
        print(f"Available operations: {', '.join(operations.keys())}")
        return
    
    result = operations[operation](num1, num2)
    
    print("=" * 50)
    print("Calculator Result")
    print("=" * 50)
    print()
    print(f"Operation: {operation.upper()}")
    print(f"Number 1:  {num1}")
    print(f"Number 2:  {num2}")
    print(f"Result:    {result}")
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()