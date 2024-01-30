import json
from collections import Counter

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def count_node_types(json_files):
    node_type_counter = Counter()

    for file_path in json_files:
        data = read_json_file(file_path)
        for entry in data:
            node_types = entry['cpp_nodetypes']
            node_type_counter.update(node_types)

    return node_type_counter

# List of JSON files
json_files = [f'output_json_objects_chunk_{i}.json' for i in range(8)]

# Count node types
node_type_counts = count_node_types(json_files)

# Save the node type counts to a JSON file
output_file_name = "node_type_counts.json"
with open(output_file_name, 'w') as output_file:
    json.dump(node_type_counts, output_file, indent=4)

print(f"Node type counts saved to {output_file_name}")
