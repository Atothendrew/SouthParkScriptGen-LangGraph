

"""
Tools Smoke Test using spgen.workflow.llm_client

This script verifies that LLM tool-calling works end-to-end via llm_client
by registering a simple example tool and prompting the model to use it.

Requirements:
- An OpenAI-compatible model with tool-calling enabled (e.g., OpenAI GPT models)
- Environment variable OPENAI_API_KEY set
- Optional: OPENAI_MODEL to choose a specific model (default: gpt-4o-mini)

Usage:
  uv run python tools/tools_smoke_test.py
  # or
  python tools/tools_smoke_test.py

Outputs:
- Prints model name and final content
- Writes tool call logs to logs/tools_smoke_test/<timestamp>/tool_calls.txt
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to Python path so we can import spgen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spgen.workflow.llm_client import llm_call, set_tool_log_dir
from tools.tool_decorators import tool_logger

FINAL_RESULT = None

@tool_logger
def set_final_result(result: str) -> bool:
    """
    Set the final result.

    Args:
        result: The final result

    Returns:
        True if the final result is set
    """
    global FINAL_RESULT
    FINAL_RESULT = result
    return True


@tool_logger
def add_numbers(a: float, b: float) -> str:
    """
    Add two numbers and return the sum as a string.

    Args:
        a: First number
        b: Second number

    Returns:
        String representation of a + b
    """
    return str(float(a) + float(b))


@tool_logger
def subtract_numbers(a: float, b: float) -> str:
    """
    Subtract two numbers and return the difference as a string.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        String representation of a - b
    """
    return str(float(a) - float(b))


@tool_logger
def multiply_numbers(a: float, b: float) -> str:
    """
    Multiply two numbers and return the product as a string.

    Args:
        a: First number
        b: Second number

    Returns:
        String representation of a * b
    """
    return str(float(a) * float(b))


@tool_logger
def divide_numbers(a: float, b: float) -> str:
    """
    Divide two numbers and return the quotient as a string.

    Args:
        a: Dividend
        b: Divisor (must not be zero)

    Returns:
        String representation of a / b
    """
    if float(b) == 0:
        return "Error: Division by zero"
    return str(float(a) / float(b))


@tool_logger
def power_numbers(base: float, exponent: float) -> str:
    """
    Raise a number to a power and return the result as a string.

    Args:
        base: The base number
        exponent: The exponent

    Returns:
        String representation of base^exponent
    """
    return str(float(base) ** float(exponent))


@tool_logger
def square_root(number: float) -> str:
    """
    Calculate the square root of a number and return the result as a string.

    Args:
        number: The number to find the square root of (must be non-negative)

    Returns:
        String representation of sqrt(number)
    """
    if float(number) < 0:
        return "Error: Cannot take square root of negative number"
    import math
    return str(math.sqrt(float(number)))


def _ensure_log_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs") / "tools_smoke_test" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)
    set_tool_log_dir(str(log_dir))
    return log_dir


def main(argv: list[str]) -> int:

    log_dir = _ensure_log_dir()
    print(f"📝 Tool logs will be written to: {log_dir}/tool_calls.txt")

    template = (
        "You are a mathematical assistant. You have these tools available:\n"
        "- add_numbers(a, b): Add two numbers\n"
        "- power_numbers(base, exponent): Raise base to exponent power\n"
        "- multiply_numbers(a, b): Multiply two numbers\n\n"
        "Task: Calculate (2 + 3) × 4²\n\n"
        "Perform these calculations step by step using the tools. Set the final result using the set_final_result tool."
    )

    # Only the tools needed for this specific calculation
    all_tools = [
        add_numbers,
        power_numbers,
        multiply_numbers,
        set_final_result
    ]

    content, model_name = llm_call(template=template, temperature=0.0, tools=all_tools)

    print(f"\n📦 Model: {model_name}")
    print("🔚 Final content:")
    print(content)

    print(f"\n✅ Finished. Inspect tool call log at: {log_dir / 'tool_calls.txt'}")

    # Calculate expected result: (2 + 3) × 4² = 5 × 16 = 80
    expected_result = (2 + 3) * (4 ** 2)  # = 80
    if not FINAL_RESULT:
        print(f"❌ Final result is not set")
        return 1
    if FINAL_RESULT != str(expected_result):
        print(f"❌ Final result is not correct: {FINAL_RESULT} != {expected_result}")
        return 1
    print(f"✅ Final result is correct: {FINAL_RESULT}")
    return 0
  


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


