"""Calculates cyclomatic complexity."""

import os
import heapq
from radon.visitors import ComplexityVisitor

def calculate_complexity(path: str) -> dict:
    """
    Calculates the average cyclomatic complexity and finds the most complex functions.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        dict: A dictionary containing the average complexity and a list of the
              top 5 most complex functions.
    """
    total_complexity = 0
    function_count = 0
    top_functions = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    visitor = ComplexityVisitor.from_code(content)
                    for func in visitor.functions:
                        total_complexity += func.complexity
                        function_count += 1
                        
                        # Use a min-heap to keep track of the top 5 largest complexity scores
                        if len(top_functions) < 5:
                            heapq.heappush(top_functions, (func.complexity, f"{file_path}:{func.lineno} - {func.name}"))
                        else:
                            heapq.heappushpop(top_functions, (func.complexity, f"{file_path}:{func.lineno} - {func.name}"))

                except Exception:
                    continue  # Ignore files that can't be read or parsed

    average_complexity = total_complexity / function_count if function_count > 0 else 0
    
    # Sort the functions from most to least complex
    sorted_top_functions = sorted(top_functions, key=lambda x: x[0], reverse=True)

    return {
        "average_complexity": round(average_complexity, 2),
        "top_complex_functions": [
            {"complexity": score, "location": location} for score, location in sorted_top_functions
        ]
    } 