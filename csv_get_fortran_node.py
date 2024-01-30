import csv
import subprocess
import tempfile
import os
import json

# Function to extract node types


def count_csv_rows(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        return sum(1 for row in csv.reader(file)) - 1  # Subtract 1 for the header

def process_csv_in_chunks(csv_file_path, chunk_size=3000):
    row_count = count_csv_rows(csv_file_path)
    print(f"Total number of rows in CSV: {row_count}")

    chunk_count = 0
    json_objects = []

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            fd, temp_cpp_file_path = tempfile.mkstemp(suffix='.cpp')
            os.close(fd)

            with open(temp_cpp_file_path, 'w') as temp_cpp_file:
                temp_cpp_file.write(row['cpp'])

            # update flang command when needed
            flang_command = f"flang-new -fc1 -fdebug-dump-parse-tree-no-sema {temp_cpp_file_path}"
            process = subprocess.Popen(flang_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            ast_dump_output, _ = process.communicate()

            # node_types = extract_node_types(ast_dump_output)

            json_object = {
                'fortran': row['fortran'],
                'cpp': row['cpp'],
                'result': row['result'],
                'reason': row['reason'],
                'fortran_ast': ast_dump_output
            }

            json_objects.append(json_object)
            os.remove(temp_cpp_file_path)
            
            # print progress every 100 rows
            if (i + 1) % 100 == 0:
                print(f"Row {i+1}: Extracted {len(ast_dump_output)} nodes of {row_count} rows.")

            # print(f"Row {i+1}: Extracted {len(node_types)} nodes")

            # Save and reset every chunk_size rows
            if (i + 1) % chunk_size == 0 or i + 1 == row_count:
                output_file_name = f'output_json_objects_chunk_{chunk_count}.json'
                with open(output_file_name, 'w') as output_file:
                    json.dump(json_objects, output_file, indent=4)
                print(f"Saved chunk {chunk_count}: Processed {i+1} rows")
                json_objects = []  # Reset the list for the next chunk
                chunk_count += 1

# update csv file path when needed
csv_file_path = "/Users/lc/Documents/Code/24ICML_data_engine/final_dataset.csv"

process_csv_in_chunks(csv_file_path)
