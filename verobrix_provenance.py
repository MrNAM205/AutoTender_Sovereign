#!/usr/bin/env python3
import os, datetime, json

LOGFILE = os.path.expanduser("~/verobrix_provenance.json")

def load_log():
    if os.path.exists(LOGFILE):
        with open(LOGFILE) as f:
            return json.load(f)
    return []

def save_log(entries):
    with open(LOGFILE, "w") as f:
        json.dump(entries, f, indent=2)

def log_event(module, message, severity="INFO"):
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "module": module,
        "severity": severity,
        "message": message
    }
    entries = load_log()
    entries.append(entry)
    save_log(entries)
    print(f"[{severity}] {timestamp} :: {module} → {message}")

# Example usage
if __name__ == "__main__":
    log_event("hygiene", "Suspicious listener found on port 11434", "WARNING")
    log_event("whitelist", "Process 'ollama' approved", "INFO")
    log_event("remediation", "DNS override applied", "ACTION")
