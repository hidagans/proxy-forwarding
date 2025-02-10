import requests
import os
import socket
import time

# Konfigurasi API CoolProxies
API_KEY = "YOURAPIKEY"  # Ganti dengan API Key kamu
API_URL = f"https://api.coolproxies.com/api.php?list=1&apikey={API_KEY}&http=1&limit=100"

# Path file konfigurasi
PROXY_FILE = "/etc/haproxy/proxy_list.txt"
HAPROXY_CONFIG = "/etc/haproxy/haproxy.cfg"

# Fungsi untuk mengecek apakah proxy bisa digunakan
def test_proxy(proxy):
    ip, port = proxy.split(":")
    try:
        sock = socket.create_connection((ip, int(port)), timeout=3)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False

# Fungsi untuk mengambil proxy baru dari API
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

# Load daftar proxy yang ada
print("📡 Mengecek proxy yang tersimpan...")
with open(PROXY_FILE, "r") as f:
    saved_proxies = f.read().splitlines()

# Periksa proxy yang masih aktif
active_proxies = []
dead_proxies = []

for proxy in saved_proxies:
    if test_proxy(proxy):
        active_proxies.append(proxy)
        print(f"✅ Proxy Aktif: {proxy}")
    else:
        dead_proxies.append(proxy)
        print(f"❌ Proxy Mati: {proxy}")

# Jika ada proxy yang mati, ambil yang baru
if dead_proxies:
    print("🔄 Mengambil proxy baru untuk menggantikan yang mati...")
    new_proxies = fetch_proxies()

    # Pastikan jumlah proxy tetap sama dengan sebelumnya
    while len(active_proxies) < len(saved_proxies) and new_proxies:
        new_proxy = new_proxies.pop(0)
        if test_proxy(new_proxy):
            active_proxies.append(new_proxy)
            print(f"🔄 Mengganti proxy dengan: {new_proxy}")

    # Simpan daftar proxy baru
    with open(PROXY_FILE, "w") as f:
        f.write("\n".join(active_proxies))

    print(f"✅ {len(active_proxies)} Proxy tersimpan di {PROXY_FILE}")

    # Perbarui konfigurasi HAProxy
    config = """\
defaults
    mode tcp
    timeout connect 5s
    timeout client 50s
    timeout server 50s
"""

    for i, proxy in enumerate(active_proxies, start=3001):
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

else:
    print("✅ Semua proxy masih aktif. Tidak ada perubahan.")

