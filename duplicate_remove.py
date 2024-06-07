import sys

def process_file(input_file_name, output_file_name):
    try:
        with open(input_file_name, 'r') as input_file:
            lines = input_file.readlines()

        processed_lines = []
        unique_strings = {}  # Maps unique strings to their lines

        for line in lines:
            processed_line = line.split(';')[0] + ';\n'
            if '=>' in processed_line:
                start_index = processed_line.find('=>') + 2
                end_index = len(processed_line)  # Assuming ';' was removed
                unique_string = processed_line[start_index:end_index].strip()
                # Store or replace the line based on the unique string
                unique_strings[unique_string] = processed_line
            else:
                processed_lines.append(processed_line)

        # Add lines with unique strings between '=>' and ';' to processed_lines
        for key in unique_strings:
            if unique_strings[key] not in processed_lines:
                processed_lines.append(unique_strings[key])

        # Writing to output, ensuring no duplicates
        final_lines = []
        for line in processed_lines:
            if line not in final_lines:
                final_lines.append(line)

        with open(output_file_name, 'w') as output_file:
            for line in final_lines:
                output_file.write(line)

        
    except IOError as e:
        print "bye"
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python script.py <input_file> <output_file>"
    else:
        input_file_name = sys.argv[1]
        output_file_name = sys.argv[2]
        process_file(input_file_name, output_file_name)