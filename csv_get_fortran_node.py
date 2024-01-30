import csv
import os
import subprocess
import tempfile
import json

def process_csv_in_chunks(csv_file_path, chunk_size=3000):
    row_count = count_csv_rows(csv_file_path)
    print(f"Total number of rows in CSV: {row_count}")

    chunk_count = 0
    json_objects = []

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            for suffix in ['.f90', '.f77', '.f']:
                fd, temp_fortran_file_path = tempfile.mkstemp(suffix=suffix)
                os.close(fd)

                with open(temp_fortran_file_path, 'w') as temp_cpp_file:
                    temp_cpp_file.write(row['fortran'])

                # update flang command when needed
                flang_command = f"flang-new -fc1 -fdebug-dump-parse-tree-no-sema {temp_fortran_file_path}"
                process = subprocess.Popen(flang_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ast_dump_output, _ = process.communicate()

                if ast_dump_output:
                    break  # Stop trying different suffixes if AST dump is not empty

                os.remove(temp_fortran_file_path)

            json_object = {
                'fortran': row['fortran'],
                'cpp': row['cpp'],
                'result': row['result'],
                'reason': row['reason'],
                'fortran_ast': ast_dump_output
            }

            json_objects.append(json_object)

            # Print progress every 100 rows
            if (i + 1) % 100 == 0:
                print(f"Row {i+1}: Extracted {len(ast_dump_output)} nodes of {row_count} rows.")

            # Save and reset every chunk_size rows
            if (i + 1) % chunk_size == 0 or i + 1 == row_count:
                output_file_name = f'output_json_objects_chunk_{chunk_count}.json'
                with open(output_file_name, 'w') as output_file:
                    json.dump(json_objects, output_file, indent=4)
                print(f"Saved chunk {chunk_count}: Processed {i+1} rows")
                json_objects = []  # Reset the list for the next chunk
                chunk_count += 1

# Helper function to count rows in a CSV file
def count_csv_rows(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        return sum(1 for _ in reader)

# Example usage:
csv_file_path = 'your_input.csv'
process_csv_in_chunks(csv_file_path)
