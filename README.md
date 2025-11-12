# Python-Based File Integrity Monitor (FIM)

A lightweight **Python File Integrity Monitoring (FIM)** tool that detects unauthorised file additions, deletions, and modifications using **SHA-256 hashing**.  

---

## Features

- **SHA-256 Hashing:** Detects any file content changes.
- **Baseline Creation:** Generates and stores a trusted baseline of file hashes.
- **Noise Suppression:** Ignores temporary and cache files via flexible glob patterns.
- **Automatic Scanning:** Optional continuous monitoring at configurable intervals.
- **JSON Event Logging:** Structured and clear logs with timestamps.

---

## How It Works

1. **Baseline Creation:**  
   Builds a JSON database of all files in the monitored folder, storing each file’s size and SHA-256 hash.

2. **Scanning:**  
   Recomputes hashes and compares them to the baseline to detect:
   - Added files  
   - Removed files  
   - Modified files

3. **Noise Suppression:**  
   Uses filename patterns (e.g., `*.tmp`, `~$*`, `__pycache__`) to filter out transient or irrelevant changes.

4. **Logging:**  
   Every event is recorded as JSON, with timestamps and event types for later analysis.

---

## Project Structure

```
fim-project/
│
├── fim.py # Main Python script
├── config.json # Configuration file
├── baseline.json # Stored baseline hashes
├── events.jsonl # JSON event log
└── README.md # You are here
```
