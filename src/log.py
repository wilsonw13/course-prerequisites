import os
import json

log_dir = "../log/"
def make_log_dir(): os.makedirs(os.path.dirname(log_dir), exist_ok=True)

def write_to_json(file_path, data):
    make_log_dir()
    with open(log_dir + file_path, "w") as f:
        json.dump(data, f, indent=4)

def append_to_file(file_path, string):
    make_log_dir()
    with open(log_dir + file_path, 'a') as f:
        f.write(string + "\n")

def clear_file(file_path):
    with open(log_dir + file_path, 'w') as f:
        f.truncate(0)
