#!/bin/bash
LOGFILE="$HOME/verobrix_diag.log"
echo "🧼 VeroBrix Offline Diagnostic — $(date)" > "$LOGFILE"

log() {
  echo "$1"
  echo "$1" >> "$LOGFILE"
}

log "🔍 Checking IP and interface status..."
ip a >> "$LOGFILE"

log "🔍 Pinging localhost..."
ping -c 3 127.0.0.1 >> "$LOGFILE"

log "🔍 Pinging default gateway..."
GATEWAY=$(ip route | grep default | awk '{print $3}')
ping -c 3 "$GATEWAY" >> "$LOGFILE"

log "🔍 Checking DNS configuration..."
cat /etc/resolv.conf >> "$LOGFILE"

log "🔍 Inspecting /etc/hosts for tampering..."
grep -i "copilot" /etc/hosts >> "$LOGFILE"

log "🔍 Reviewing firewall rules..."
sudo iptables -L >> "$LOGFILE"

log "🔍 Checking proxy environment variables..."
env | grep -i proxy >> "$LOGFILE"

log "✅ Diagnostic complete. Log saved to $LOGFILE"