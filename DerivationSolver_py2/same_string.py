import sys

def separate_and_filter_lines(lines):
    lines_with_arrow = []
    lines_without_arrow = []
    unique_strings = set()

    # Separate lines with and without '=>'
    for line in lines:
        if '=>' in line:
            start_index = line.find('=>') + 2
            end_index = line.find(';', start_index)
            unique_string = line[start_index:end_index].strip()
            unique_strings.add(unique_string)
            lines_with_arrow.append(line)
        else:
            lines_without_arrow.append(line)

    # Filter out lines without '=>' that match any unique string
    filtered_lines_without_arrow = [
        line for line in lines_without_arrow if line.split(';')[0].strip() not in unique_strings
    ]

    return lines_with_arrow, filtered_lines_without_arrow

def process_file(input_file_name, output_file_name):
    try:
        with open(input_file_name, 'r') as input_file:
            lines = input_file.readlines()

        lines_with_arrow, lines_without_arrow = separate_and_filter_lines(lines)

        with open(output_file_name, 'w') as output_file:
            #output_file.write("Lines with '=>':\n")
            for line in lines_with_arrow:
                output_file.write(line)
            #output_file.write("\nLines without '=>':\n")
            for line in lines_without_arrow:
                output_file.write(line)

    except IOError as e:
        print "An error occurred:", e

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: python script.py <input_file> <output_file>"
    else:
        input_file_name = sys.argv[1]
        output_file_name = sys.argv[2]
        process_file(input_file_name, output_file_name)