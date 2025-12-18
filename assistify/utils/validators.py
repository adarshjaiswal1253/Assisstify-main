"""
Utility functions for calculator, validators, and common operations.
"""

import re
import math


def safe_eval(expr):
    """
    Safely evaluate mathematical expressions with allowed operations.
    
    Args:
        expr (str): Mathematical expression
        
    Returns:
        float or None: Result of calculation or None if invalid
    """
    if not re.match(r"^[\d+\-*/().\s]+$", expr):
        return None
    try:
        result = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "pow": pow})
        return result
    except Exception:
        return None


def parse_math_expression(text):
    """
    Convert natural language to mathematical expression.
    
    Args:
        text (str): Natural language input
        
    Returns:
        str: Mathematical expression
    """
    expr = text.replace("plus", "+").replace("add", "+")
    expr = expr.replace("minus", "-").replace("subtract", "-")
    expr = expr.replace("times", "*").replace("multiply", "*").replace("x", "*")
    expr = expr.replace("divide", "/").replace("divided by", "/")
    expr = expr.replace("power", "**").replace("^", "**")
    return expr


def extract_name_from_input(text):
    """
    Extract name from "my name is ..." pattern.
    
    Args:
        text (str): User input
        
    Returns:
        str or None: Extracted name or None
    """
    match = re.search(r"my name is (.+)", text.lower())
    if match:
        return match.group(1).strip().title()
    return None


def extract_task_number(text):
    """
    Extract task number from delete task commands.
    
    Args:
        text (str): User input
        
    Returns:
        int or None: Task number (1-indexed) or None
    """
    match = re.search(r"delete task (\d+)", text.lower())
    if match:
        return int(match.group(1))
    return None
