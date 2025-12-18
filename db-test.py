import time
import requests

BASE_URL = "http://localhost:8000"

def wait_api():
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False

def main():
    if not wait_api():
        raise SystemExit("API not reachable on http://localhost:8000")

    r = requests.get(f"{BASE_URL}/health/db")
    print("DB health:", r.status_code, r.json())

    payload = {"name": "test-from-db-test"}
    r = requests.post(f"{BASE_URL}/items", json=payload)
    print("POST /items:", r.status_code, r.json())
    r.raise_for_status()

    r = requests.get(f"{BASE_URL}/items")
    print("GET /items:", r.status_code, r.json())
    r.raise_for_status()

    items = r.json()
    assert any(i["name"] == payload["name"] for i in items), "Inserted item not found!"
    print("✅ OK: API can write/read SQLite")

if __name__ == "__main__":
    main()
