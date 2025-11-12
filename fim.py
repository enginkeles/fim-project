import os
import hashlib
import sys
import json
import fnmatch
import time
from datetime import datetime

with open("config.json") as f:
    cfg = json.load(f)

folder_to_monitor = cfg["folder_to_monitor"]
baseline_file = cfg["baseline_path"]
log_file = cfg["events_log"]
ignore_globs = set(cfg["ignore_globs"])
autoscan_secs = int(cfg["autoscan_secs"])

def should_ignore(path):
    base = os.path.basename(path)
    for ptrn in ignore_globs:
        if fnmatch.fnmatch(path, ptrn) or fnmatch.fnmatch(base, ptrn):
            return True
    return False

def log_event(event_type, **details):
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "event": event_type,
        **details
    }

    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as lf:
        lf.write(json.dumps(record, ensure_ascii=False) + "\n")

def auto_scan():
    if not os.path.exists(baseline_file) or os.path.getsize(baseline_file) == 0:
        print("No baseline found. Creating.")
        collect_baseline()

    print(f"Auto-scan running every {autoscan_secs}s. Press Ctrl+C to stop.")
    log_event("auto_scan_started", interval_seconds=autoscan_secs)

    try:
        while True:
            t0 = time.time()
            scan_changes()
            elapsed = time.time() - t0
            pause = max(0, autoscan_secs - elapsed)
            time.sleep(pause)
    except KeyboardInterrupt:
        print("\nAutoscan stopped.")
        log_event("auto_scan_stopped")


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
                if should_ignore(file_path):
                    log_event("suppressed", path=file_path, reason="ignore_glob")
                    continue
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

    log_event(
        "baseline_created",
        folder=folder_to_monitor,
        file_count=len(baseline_data)
    )

def scan_changes():
    if not os.path.exists(baseline_file) or os.path.getsize(baseline_file) == 0:
        print("Baseline not found - creating new baseline.")
        collect_baseline()

    log_event("scan_started", folder=folder_to_monitor)
    
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
        log_event(
            "scan_summary",
            folder=folder_to_monitor,
            counts={
                "added": len(added_files),
                "removed": len(removed_files),
                "modified": len(modified_files)
            }
        )
    else:
        print(changes)
        log_event(
            "scan_summary",
            folder=folder_to_monitor,
            counts={
                "added": len(added_files),
                "removed": len(removed_files),
                "modified": len(modified_files)
            }
        )

        for path in added_files:
            log_event("file_added", path=path)
        for path in removed_files:
            log_event("file_removed", path=path)
        for path in modified_files:
            log_event("file_modified", path=path)


def main():
    while True:
        print("\nFile Integrity Monitor")
        print("[a] Autoscan")
        print("[b] Build baseline")
        print("[s] Scan for changes")
        print("[e] Exit")
        choice = input("Enter choice: ").lower().strip()

        if choice == "a":
            auto_scan()
        elif choice == "b":
            collect_baseline()
        elif choice == "s":
            scan_changes()
        elif choice == "e":
            sys.exit(0)
        else:
            print("Please choose either b, s, or e")

if __name__ == "__main__":
    main()