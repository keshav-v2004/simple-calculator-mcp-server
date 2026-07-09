import sympy as sp
from fastmcp import FastMCP
import re
import math

mcp = FastMCP("advanced-math-server")

# Server-side memory storage for variables and calculation history
MEMORY = {"ans": 0.0}
HISTORY = []

@mcp.tool
async def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a (int): The first number to add.
        b (int): The second number to add.

    Returns:
        int: The sum of a and b.

    """
    return a + b

@mcp.tool
async def subtract(a: int, b: int) -> int:
    """
    Subtract one number from another.

    Args:
        a (int): The number to subtract from.
        b (int): The number to subtract.

    Returns:
        int: The difference of a and b.

    """
    return a - b

@mcp.tool
async def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a (int): The first number to multiply.
        b (int): The second number to multiply.

    Returns:
        int: The product of a and b.

    """
    return a * b

@mcp.tool
async def divide(a: int, b: int) -> int:
    """
    Divide one number by another.

    Args:
        a (int): The number to divide.
        b (int): The number to divide by.

    Returns:
        int: The quotient of a and b.

    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a // b

@mcp.tool
async def power(base: float, exponent: float) -> float:
    """Raise a base number to an exponent."""
    return math.pow(base, exponent)

@mcp.tool
async def square_root(x: float) -> float:
    """Calculate the square root of a positive number."""
    if x < 0:
        raise ValueError("Cannot calculate the square root of a negative number.")
    return math.sqrt(x)

@mcp.tool
async def modulo(a: float, b: float) -> float:
    """Calculate the remainder of division (a % b)."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a % b

def preprocess_expression(expr_str: str) -> str:
    """
    Pre-processes common natural language math shorthand inputs into standard Python notation.
    Example: 'x3 + 5*x2' becomes 'x**3 + 5*x**2'
    """
    if not expr_str:
        return expr_str
        
    # Replace a letter followed directly by a number (e.g., x3 -> x**3, y2 -> y**2)
    # [a-zA-Z] matches any single variable letter
    # (\d+) matches one or more sequential digits
    processed = re.sub(r'([a-zA-Z])(\d+)', r'\1**\2', expr_str)
    
    return processed

@mcp.tool()
async def evaluate_expression(expression: str, variables: dict = None) -> str:
    """
    Parses and evaluates a complex mathematical string expression.
    Supports standard operators, functions (sin, cos, log, sqrt, pi), and custom variables.
    """
    try:
        clean_expr = preprocess_expression(expression)
        context = {**MEMORY, **(variables or {})}
        expr = sp.sympify(clean_expr)
        result = expr.subs(context).evalf()
        
        MEMORY["ans"] = float(result) if result.is_number else result
        HISTORY.append(f"{expression} = {result}")
        
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

@mcp.tool()
async def solve_equation(equation_str: str, variable_to_solve: str = "x") -> str:
    """Solves an algebraic equation set to 0."""
    try:
        clean_eq = preprocess_expression(equation_str)
        var = sp.Symbol(variable_to_solve)
        expr = sp.sympify(clean_eq)
        solutions = sp.solve(expr, var)
        return f"Solutions for {variable_to_solve}: {solutions}"
    except Exception as e:
        return f"Error solving equation: {str(e)}"

@mcp.tool()
async def compute_calculus(expression: str, operation: str = "derivative", variable: str = "x") -> str:
    """Performs symbolic calculus operations: derivatives or integrals."""
    try:
        clean_expr = preprocess_expression(expression)
        var = sp.Symbol(variable)
        expr = sp.sympify(clean_expr)
        
        if operation.lower() == "derivative":
            result = sp.diff(expr, var)
            return f"d/d{variable} ({expression}) = {result}"
        elif operation.lower() == "integral":
            result = sp.integrate(expr, var)
            return f"Integral of ({expression}) d{variable} = {result} + C"
        else:
            return "Invalid operation. Choose 'derivative' or 'integral'."
    except Exception as e:
        return f"Calculus error: {str(e)}"

@mcp.tool()
async def store_variable(name: str, value: float) -> str:
    """Stores a numeric value in the server's persistent memory."""
    if name.lower() in ["pi", "e", "i"]:
        return f"Error: '{name}' is a reserved mathematical constant."
    MEMORY[name] = value
    return f"Stored variable: {name} = {value}"

@mcp.tool()
async def get_history_and_memory() -> dict:
    """Returns the current stored variables and the log of previous calculations."""
    return {
        "stored_variables": {k: str(v) for k, v in MEMORY.items()},
        "recent_history": HISTORY[-10:]
    }

if __name__ == '__main__':
    
    import os
    

    port = int(os.environ.get("PORT", 8000))
    

    mcp.run(transport='sse', host='0.0.0.0', port=port)


