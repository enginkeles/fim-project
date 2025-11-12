import os
import hashlib
import sys
import json

with open("config.json") as f:
    cfg = json.load(f)
folder_to_monitor = cfg["folder_to_monitor"]
baseline_file = cfg["baseline_path"]

def get_hash(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def store_file_data(folder_to_monitor):
    data = {}

    with os.scandir(folder_to_monitor) as entries:
        for entry in entries:
            if entry.is_file():
                file_path = os.path.abspath(entry.path)
                file_size = os.path.getsize(file_path)
                file_hash = get_hash(file_path)

                data[file_path] = {
                    "size": file_size,
                    "hash": file_hash
                }

    return data

def collect_baseline():
    baseline_data = store_file_data(folder_to_monitor)
    with open(baseline_file, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=4)
    
    print("Baseline created.")

def scan_changes():
    if not os.path.exists(baseline_file) or os.path.getsize(baseline_file) == 0:
        print("Baseline not found - creating new baseline.")
        collect_baseline()
    
    with open(baseline_file, "r", encoding="utf-8") as f:
        baseline = json.load(f)
    
    current = store_file_data(folder_to_monitor)
    baseline_paths = set(baseline.keys())
    current_paths = set(current.keys())

    added_files = []
    removed_files = []
    modified_files = []

    for path in current_paths:
        if path not in baseline_paths:
            added_files.append(path)
    
    for path in baseline_paths:
        if path not in current_paths:
            removed_files.append(path)
    
    for path in baseline_paths.intersection(current_paths):
        old = baseline[path]
        new = current[path]
        if old["size"] != new["size"] or old["hash"] != new["hash"]:
            modified_files.append(path)

    changes = {
        "added": added_files,
        "removed": removed_files,
        "modified": modified_files
    }

    if not added_files and not removed_files and not modified_files:
        print("No changes detected.")
    else:
        print(changes)

def main():
    while True:
        print("\nFile Integrity Monitor")
        print("[b] Build baseline")
        print("[s] Scan for changes")
        print("[e] Exit")
        choice = input("Enter choice: ").lower().strip()

        if choice == "b":
            collect_baseline()
        elif choice == "s":
            scan_changes()
        elif choice == "e":
            sys.exit(0)
        else:
            print("Please choose either b, s, or e")

if __name__ == "__main__":
    main()