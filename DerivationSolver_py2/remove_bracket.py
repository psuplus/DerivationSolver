import re
import sys

def process_line(line):
    parts = line.split(';')
    line = parts[0] + ';' if len(parts) > 1 else parts[0]

    bracketed_parts = re.findall(r'\[.*?\]', line)

    for part in bracketed_parts:
        if 'CONST' in line.split(part)[0]:
            modified_part = re.sub(r'S', 'H', part)
            modified_part = re.sub(r'P', 'L', modified_part)
            modified_part = ''.join(re.findall(r'[HL]', modified_part))
            line = line.replace('CONST' + part, modified_part)
        else:
            line = line.replace(part, '')

    return line

def remove_brackets_and_text_after_semicolon(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        modified_lines.append(process_line(line))

    with open(output_file_path, 'w') as file:
        for line in modified_lines:
            file.write(line + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    remove_brackets_and_text_after_semicolon(input_file, output_file)
