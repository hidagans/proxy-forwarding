import requests
import socket
import time

API_KEY = "YOURAPIKEY"
API_URL = f"https://api.coolproxies.com/api.php?list=1&apikey={API_KEY}&http=1"

PROXY_LIST_FILE = "/etc/haproxy/proxy_list.txt"
TIMEOUT = 5  # Waktu maksimal pengecekan proxy

def test_proxy(proxy):
    try:
        ip, port = proxy.split(":")
        with socket.create_connection((ip, int(port)), timeout=TIMEOUT):
            return True
    except:
        return False

def get_new_proxies():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            proxies = response.text.split("\n")
            return [p.strip() for p in proxies if p.strip()]
    except Exception as e:
        print(f"Error fetching new proxies: {e}")
    return []

def replace_dead_proxies():
    with open(PROXY_LIST_FILE, "r") as f:
        old_proxies = [line.strip() for line in f.readlines()]

    new_proxies = get_new_proxies()
    working_proxies = []

    for proxy in old_proxies:
        if test_proxy(proxy):
            working_proxies.append(proxy)
        else:
            print(f"❌ Proxy mati: {proxy}")
            if new_proxies:
                new_proxy = new_proxies.pop(0)
                print(f"🔄 Mengganti dengan proxy baru: {new_proxy}")
                working_proxies.append(new_proxy)

    with open(PROXY_LIST_FILE, "w") as f:
        for proxy in working_proxies:
            f.write(proxy + "\n")

    print(f"✅ Proxy list diperbarui ({len(working_proxies)} aktif)")

if __name__ == "__main__":
    replace_dead_proxies()
