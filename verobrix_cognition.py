#!/usr/bin/env python3
import json, os
from datetime import datetime

LOGFILE = os.path.expanduser("~/verobrix_provenance.json")

def load_provenance():
    if not os.path.exists(LOGFILE):
        return []
    with open(LOGFILE) as f:
        return json.load(f)

def detect_contradictions(entries):
    seen = {}
    contradictions = []
    for entry in entries:
        key = entry["message"]
        if key in seen:
            prev = seen[key]
            if prev["severity"] != entry["severity"]:
                contradictions.append({
                    "message": key,
                    "first": prev,
                    "second": entry
                })
        else:
            seen[key] = entry
    return contradictions

def narrate_contradictions(contradictions):
    for c in contradictions:
        print(f"⚠️ Contradiction detected:")
        print(f"  → {c['first']['severity']} @ {c['first']['timestamp']} :: {c['first']['module']}")
        print(f"  → {c['second']['severity']} @ {c['second']['timestamp']} :: {c['second']['module']}")
        print(f"  ✎ Message: {c['message']}\n")

def main():
    entries = load_provenance()
    contradictions = detect_contradictions(entries)
    if contradictions:
        narrate_contradictions(contradictions)
    else:
        print("✅ No contradictions detected. Cognition loop is clean.")

if __name__ == "__main__":
    main()
