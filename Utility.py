"""
This module provides utility functions for generating unique IDs and 
splitting strings into multiple lines based on a maximum number of characters.

Imports:
- uuid: For generating unique identifiers.

Functions:
- generate_unique_id(): Generates and returns a unique ID as a string.
- split_string(string: str, max_characters: int): Splits a string into lines 
  that do not exceed the specified number of characters.

Returns:
- str: A unique identifier.
- str: A string with line breaks inserted to ensure no line exceeds the 
  specified number of characters.

Author: Blake Stevenson
Date: 2024-09-06
Version: 1.0
License: MIT
"""

import uuid


def generate_unique_id() -> str:
    """
    Generates and returns a unique ID as a string.
    """
    return str(uuid.uuid4())


def split_string(string: str, max_characters: int) -> str:
    """
    Splits a string into lines that do not exceed the specified number of characters.
    """
    lines = []
    current_line = ""

    for word in string.split():
        if len(current_line) + len(word) + 1 <= max_characters:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())

    return '\n'.join(lines)
