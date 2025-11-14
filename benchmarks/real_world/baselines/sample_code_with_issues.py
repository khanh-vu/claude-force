"""Sample code with various quality and security issues for benchmarking."""

import os
import pickle


def process_user_data(user_input):
    """Process user data - has several issues."""
    # Security issue: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Quality issue: Bare except
    try:
        result = execute_query(query)
    except:
        pass

    # Security issue: Using eval
    config = eval(user_input)

    # Security issue: Hardcoded password
    db_password = "admin123"

    # Quality issue: Unused variable
    temp_var = "unused"

    # Quality issue: No error handling
    file_data = open("/tmp/data.txt").read()

    # Security issue: Pickle loading untrusted data
    user_obj = pickle.loads(user_input)

    return result


def execute_query(query):
    """Execute database query."""
    # Stub implementation
    return []


def calculate_total(items):
    """Calculate total - missing docstring details."""
    total = 0
    for item in items:
        total = total + item["price"]
    return total


# Quality issue: Function too complex
def complex_function(a, b, c, d, e):
    """Very complex function."""
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return "too nested"
    return "ok"
