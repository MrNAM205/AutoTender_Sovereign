#!/usr/bin/env python3
import json, re, datetime

DEFINITIONS_FILE = "ucc_definitions.json"
COUPON_FILE = "sample_coupon.txt"
LOGFILE = "verobrix_legal.log"

def log_event(event):
    timestamp = datetime.datetime.now().isoformat()
    entry = f"[LEGAL] {timestamp} :: {event}"
    print(entry)
    with open(LOGFILE, "a") as log:
        log.write(entry + "\n")

def load_definitions():
    try:
        with open(DEFINITIONS_FILE) as f:
            return json.load(f)
    except:
        log_event("⚠️ Failed to load UCC definitions.")
        return {}

def scan_coupon(text, definitions):
    findings = []
    for term, definition in definitions.items():
        if term.lower() in text.lower():
            findings.append((term, definition))
    return findings

def detect_contradictions(text):
    contradictions = []
    if "payment due" in text and "remittance enclosed" in text:
        contradictions.append("⚠️ Coupon contains both 'payment due' and 'remittance enclosed'.")
    if "amount owed" in text and "zero balance" in text:
        contradictions.append("⚠️ Coupon contradicts itself on balance status.")
    return contradictions

def main():
    log_event("🧠 Launching Legal Intelligence Module...")
    definitions = load_definitions()

    if not definitions:
        return

    try:
        with open(COUPON_FILE) as f:
            coupon_text = f.read()
    except:
        log_event("⚠️ Failed to load sample coupon.")
        return

    findings = scan_coupon(coupon_text, definitions)
    contradictions = detect_contradictions(coupon_text)

    for term, definition in findings:
        log_event(f"📘 Found term: '{term}' → {definition}")

    for contradiction in contradictions:
        log_event(contradiction)

    log_event("✅ Legal scan complete.")

if __name__ == "__main__":
    main()
