#!/bin/bash

# Check for input argument
if [ "$#" -ne 1 ]; then
    echo "Usage: ./run_pipeline.sh <filename.con>"
    exit 1
fi

INPUT_FILE="../tests/$1"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' does not exist."
    exit 1
fi

# Get the base name without extension
BASENAME=$(basename "$INPUT_FILE" .con)
OUTPUT_FILE="../tests/${BASENAME}_nobr.con"

# Step 1: Run remove_bracket.py
echo "Running remove_bracket.py on $INPUT_FILE..."
python remove_bracket.py "$INPUT_FILE" "$OUTPUT_FILE"

# Step 2: Run solver.py on the output file
echo "Running solver.py on $OUTPUT_FILE..."
python test_solver.py "$OUTPUT_FILE"