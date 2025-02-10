#!/bin/bash

echo "🚀 Installing HAProxy & Proxy Manager..."

# Update dan install HAProxy
apt update && apt install -y haproxy python3

# Buat file daftar proxy
PROXY_FILE="/etc/haproxy/proxy_list.txt"
echo "Contoh format: IP:PORT" > $PROXY_FILE
echo "Masukkan daftar proxy ke $PROXY_FILE"

# Buat script auto-config
cat <<EOF > /etc/haproxy/generate_haproxy.py
import os

proxy_file = "/etc/haproxy/proxy_list.txt"
haproxy_config = "/etc/haproxy/haproxy.cfg"

with open(proxy_file, "r") as f:
    proxies = [line.strip() for line in f.readlines() if line.strip()]

config = """\
defaults
    mode tcp
    timeout connect 5s
    timeout client 50s
    timeout server 50s

"""

for i, proxy in enumerate(proxies, start=3001):
    ip, port = proxy.split(":")
    config += f"""
frontend proxy_{i}
    bind *:{i}
    default_backend proxy_{i}

backend proxy_{i}
    server proxy {ip}:{port} check
"""

with open(haproxy_config, "w") as f:
    f.write(config)

os.system("systemctl restart haproxy")
print("✅ HAProxy config updated & restarted!")
EOF

# Set cronjob agar update otomatis
(crontab -l ; echo "*/5 * * * * python3 /etc/haproxy/generate_haproxy.py") | crontab -

# Restart HAProxy
python3 /etc/haproxy/generate_haproxy.py

echo "✅ Installation completed! Edit /etc/haproxy/proxy_list.txt & restart HAProxy!"
