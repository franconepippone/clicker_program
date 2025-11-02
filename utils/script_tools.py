import re


def add_offset_to_move_commands(script_lines, x_offset, y_offset):

    move_cmd_pattern = re.compile(r'^(move)\s+(-?\d+)\s+(-?\d+)(.*)$')
    updated_lines = []

    for line in script_lines:
        match = move_cmd_pattern.match(line)
        if match:
            cmd, x_str, y_str, rest = match.groups()
            x = int(x_str) + x_offset
            y = int(y_str) + y_offset
            updated_line = f"{cmd} {x} {y}{rest}"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    return updated_lines