#!/bin/bash
LOGFILE="$HOME/verobrix_remediate.log"
echo "🛠️ VeroBrix Remediation Agent — $(date)" > "$LOGFILE"

log() {
  echo "$1"
  echo "$1" >> "$LOGFILE"
}

log "🔧 Re-enabling network interface..."
INTERFACE=$(ip link | grep -E 'eth0|wlan0' | awk -F: '{print $2}' | head -n1 | xargs)
sudo ip link set "$INTERFACE" up
sudo dhclient "$INTERFACE"

log "🌐 Resetting DNS configuration..."
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf > /dev/null
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf > /dev/null

log "🧱 Flushing firewall rules..."
sudo iptables -F
sudo iptables -X

log "🔄 Restarting network stack..."
sudo systemctl restart NetworkManager

log "✅ Remediation complete. Log saved to $LOGFILE"