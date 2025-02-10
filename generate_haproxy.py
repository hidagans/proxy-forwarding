import requests
import os
import time
import socket

# Konfigurasi API CoolProxies
API_KEY = "YOURAPIKEY"  # Ganti dengan API Key kamu
API_URL = f"https://api.coolproxies.com/api.php?list=1&apikey={API_KEY}&http=1&limit=100"

# Path file konfigurasi HAProxy
PROXY_FILE = "/etc/haproxy/proxy_list.txt"
HAPROXY_CONFIG = "/etc/haproxy/haproxy.cfg"

# Fungsi untuk mengambil proxy dari API
def fetch_proxies():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            print("❌ Gagal mengambil proxy dari API!")
            return []
    except requests.RequestException as e:
        print(f"❌ Error mengambil proxy: {e}")
        return []

# Fungsi untuk mengecek apakah proxy bisa digunakan
def test_proxy(proxy):
    ip, port = proxy.split(":")
    try:
        sock = socket.create_connection((ip, int(port)), timeout=3)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False

# Ambil daftar proxy dari API
print("📡 Mengambil daftar proxy...")
proxies = fetch_proxies()
valid_proxies = []

# Uji setiap proxy
print("⏳ Menguji proxy yang berfungsi...")
for proxy in proxies:
    if test_proxy(proxy):
        valid_proxies.append(proxy)
        print(f"✅ Proxy Berfungsi: {proxy}")
    else:
        print(f"❌ Proxy Gagal: {proxy}")

# Simpan proxy yang valid ke file
with open(PROXY_FILE, "w") as f:
    f.write("\n".join(valid_proxies))

print(f"📌 {len(valid_proxies)} Proxy tersimpan di {PROXY_FILE}")

# Buat ulang konfigurasi HAProxy
config = """\
defaults
    mode tcp
    timeout connect 5s
    timeout client 50s
    timeout server 50s
"""

for i, proxy in enumerate(valid_proxies, start=3001):
    ip, port = proxy.split(":")
    config += f"""
frontend proxy_{i}
    bind *:{i}
    default_backend proxy_{i}

backend proxy_{i}
    server proxy {ip}:{port} check
"""

# Simpan konfigurasi baru ke HAProxy
with open(HAPROXY_CONFIG, "w") as f:
    f.write(config)

# Restart HAProxy agar perubahan diterapkan
os.system("systemctl restart haproxy")
print("🚀 HAProxy diperbarui & di-restart!")
