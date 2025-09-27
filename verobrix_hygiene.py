#!/usr/bin/env python3
import os, subprocess, hashlib, datetime, json

LOGFILE = os.path.expanduser("~/verobrix_hygiene.log")
WHITELIST_FILE = os.path.expanduser("~/verobrix_whitelist.json")

def log_event(event, severity="INFO"):
    timestamp = datetime.datetime.now().isoformat()
    entry = f"[{severity}] {timestamp} :: {event}"
    print(entry)
    with open(LOGFILE, "a") as log:
        log.write(entry + "\n")

def load_whitelist():
    try:
        with open(WHITELIST_FILE) as f:
            return json.load(f)
    except:
        return {"processes": [], "ports": [], "scripts": []}

WHITELIST = load_whitelist()

def is_whitelisted(item, category):
    return item in WHITELIST.get(category, [])

def scan_processes():
    log_event("🔍 Scanning active processes...")
    output = subprocess.getoutput("ps aux")
    for line in output.splitlines():
        for susp in ["wget", "curl", "nc", "python3 -c", "sh -c", "/tmp"]:
            if susp in line:
                proc_name = line.split()[10] if len(line.split()) > 10 else line
                if is_whitelisted(proc_name, "processes"):
                    log_event(f"🟢 Whitelisted process: {proc_name}", "INFO")
                else:
                    log_event(f"⚠️ Suspicious process: {line}", "WARNING")

def check_crontab():
    log_event("🔍 Checking crontab entries...")
    output = subprocess.getoutput("crontab -l")
    for line in output.splitlines():
        if "@reboot" in line or "wget" in line or "curl" in line:
            log_event(f"⚠️ Suspicious crontab: {line}", "WARNING")

def check_startup_scripts():
    log_event("🔍 Auditing startup scripts...")
    paths = ["/etc/init.d", "/etc/systemd/system", "/etc/rc.local"]
    for path in paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    if is_whitelisted(full_path, "scripts"):
                        log_event(f"🟢 Whitelisted script: {full_path}", "INFO")
                        continue
                    try:
                        content = open(full_path).read()
                        if "wget" in content or "curl" in content:
                            log_event(f"⚠️ Suspicious startup script: {full_path}", "WARNING")
                    except: pass

def check_network():
    log_event("🔍 Checking network listeners...")
    output = subprocess.getoutput("ss -tulnp")
    for line in output.splitlines():
        if "LISTEN" in line and "0.0.0.0" in line:
            port = line.split()[4].split(":")[-1]
            if is_whitelisted(port, "ports"):
                log_event(f"🟢 Whitelisted port: {port}", "INFO")
            else:
                log_event(f"⚠️ Open listener: {line}", "WARNING")

def check_users():
    log_event("🔍 Auditing user accounts...")
    output = subprocess.getoutput("cat /etc/passwd")
    for line in output.splitlines():
        if "/bin/bash" in line and not line.startswith("root"):
            log_event(f"👤 Shell user: {line}", "INFO")

def main():
    log_event("🧼 Launching VeroBrix Hygiene Agent...")
    scan_processes()
    check_crontab()
    check_startup_scripts()
    check_network()
    check_users()
    log_event("✅ Hygiene scan complete. Log saved to " + LOGFILE)

if __name__ == "__main__":
    main()
