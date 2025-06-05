"""Calculates cyclomatic complexity."""

import os
from radon.visitors import ComplexityVisitor
from radon.raw import analyze

def calculate_complexity(path: str) -> float:
    """
    Calculates the average cyclomatic complexity of Python files in a given path.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        float: The average cyclomatic complexity.
    """
    total_complexity = 0
    file_count = 0

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Using radon to calculate complexity
                    visitor = ComplexityVisitor.from_code(content)
                    total_complexity += sum(func.complexity for func in visitor.functions)
                    file_count += 1
                except Exception:
                    continue  # Ignore files that can't be read or parsed

    if file_count == 0:
        return 0.0

    return total_complexity / file_count 