import requests

API_KEY = "YOURAPIKEY"  # Ganti dengan API key kamu
API_URL = f"https://api.coolproxies.com/api.php?list=1&apikey={API_KEY}&http=1"

PROXY_LIST_FILE = "/etc/haproxy/proxy_list.txt"

def get_proxies():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            proxies = response.text.split("\n")
            proxies = [p.strip() for p in proxies if p.strip()]
            return proxies
    except Exception as e:
        print(f"Error fetching proxies: {e}")
    return []

def save_proxies(proxies):
    with open(PROXY_LIST_FILE, "w") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    print(f"✅ Saved {len(proxies)} proxies to {PROXY_LIST_FILE}")

if __name__ == "__main__":
    proxies = get_proxies()
    if proxies:
        save_proxies(proxies)
    else:
        print("❌ No proxies found!")
