import os
import json


def ensure_dirs(path): os.makedirs(os.path.dirname(path), exist_ok=True)


def write_to_json_dir(file_path, data, type: str="json"):
    init_path = "./json/"
    path = init_path + file_path

    ensure_dirs(path) # creates dir if doesn't exist
    with open(path, "w", encoding="utf-8") as f:
        if type == "json":
            json.dump(data, f, indent=4)
        elif type == "txt":
            f.write(data)
        else:
            print(f"Writing to unknown file type: {type}")

def get_from_json_dir(file_path):
    init_path = "./json/"
    path = init_path + file_path

    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("File not found: " + path)
    except json.JSONDecodeError:
        print("Invalid JSON format in file: " + path)


def get_config():
    return get_from_json_dir("config/server_config.json")


def append_to_log_file(file_path, string):
    init_path = "./log/"
    path = init_path + file_path

    ensure_dirs(path) # creates dir if doesn't exist
    with open(path, 'a', encoding="utf-8") as f:
        f.write(string + "\n")


def clear_log_dir():
    # Set the directory path
    directory = './log/'

    ensure_dirs(directory)

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
