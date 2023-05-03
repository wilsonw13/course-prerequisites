import os
import json

def ensure_dirs(path): os.makedirs(os.path.dirname(path), exist_ok=True)

def write_to_datasets_json(file_path, data):
    init_path = "../datasets/"
    ensure_dirs(init_path + file_path)
    with open(init_path + file_path, "w") as f:
        json.dump(data, f, indent=4)

def append_to_log_file(file_path, string):
    init_path = "../log/"
    ensure_dirs(init_path + file_path)
    with open(init_path + file_path, 'a') as f:
        f.write(string + "\n")

def clear_log_dir():
    # Set the directory path
    directory = '../log/'

    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        # Build the full file path
        file_path = os.path.join(directory, filename)

        # Check if the file is a file (not a directory) and has a .txt extension
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            # Open the file in write mode and truncate its content
            with open(file_path, 'w') as f:
                f.truncate(0)

def clear_file(file_path):
    ensure_dirs(file_path)
    with open(file_path, 'w') as f:
        f.truncate(0)
