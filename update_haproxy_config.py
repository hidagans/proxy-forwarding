import os

PROXY_LIST_FILE = "/etc/haproxy/proxy_list.txt"
HAPROXY_TEMPLATE = "/etc/haproxy/haproxy_template.cfg"
HAPROXY_CONFIG = "/etc/haproxy/haproxy.cfg"

def generate_haproxy_config():
    try:
        # Baca daftar proxy dari file
        with open(PROXY_LIST_FILE, "r") as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]

        # Buat daftar server proxy
        proxy_servers = "\n    ".join(
            [f"server proxy{i+1} {proxy} check" for i, proxy in enumerate(proxies)]
        )

        # Baca template dan ganti placeholder {PROXY_SERVERS}
        with open(HAPROXY_TEMPLATE, "r") as f:
            haproxy_config = f.read().replace("{PROXY_SERVERS}", proxy_servers)

        # Simpan konfigurasi baru
        with open(HAPROXY_CONFIG, "w") as f:
            f.write(haproxy_config)

        print(f"✅ Updated HAProxy config with {len(proxies)} proxies")

        # Restart HAProxy agar konfigurasi baru aktif
        os.system("systemctl restart haproxy")

    except Exception as e:
        print(f"❌ Error updating HAProxy config: {e}")

if __name__ == "__main__":
    generate_haproxy_config()
