def split_string(string: str, max_characters: int):
    words = string.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_characters:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())

    return '\n'.join(lines)