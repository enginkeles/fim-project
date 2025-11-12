import os
import hashlib
import sys
import json

# Baseline should initially store file path, size and hash.
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


def collect_baseline():
    baseline_data = []

    with os.scandir(folder_to_monitor) as entries:
        for entry in entries:
            if entry.is_file():
                file_path = os.path.abspath(entry.path)
                file_size = os.path.getsize(file_path)
                file_hash = get_hash(file_path)

                baseline_data.append({
                    "path": file_path,
                    "size": file_size,
                    "hash": file_hash
                })
    with open(baseline_file, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=4)


def scan_changes():
    print("Changes scanned.")

def main():
    print("\nFile Integrity Monitor")
    print("[b] Build baseline")
    print("[s] Scan for changes")
    print("[e] Exit")

    while True:
        choice = input("Enter choice: ").lower()
        if choice in ("b", "s", "e"):
            break
        print("Please choose either b, s, or e")

    if choice == "b":
        collect_baseline()
    if choice == "s":
        scan_changes()
    if choice == "e":
        sys.exit(0)

if __name__ == "__main__":
    main()