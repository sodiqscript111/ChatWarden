import urllib.request
import json
import urllib.error

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as f:
            return f.status, json.loads(f.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 500, str(e)

def test():
    base = "http://localhost:8001"
    
    print("--- Testing API on Port 8001 ---")
    
    # Health
    print("Testing /health...")
    try:
        with urllib.request.urlopen(f"{base}/health") as f:
            print(f"Health: {f.status} {f.read().decode('utf-8')}")
    except Exception as e:
        print(f"Health failed: {e}")

    # Clean
    print("\nTesting /moderate (Clean)...")
    code, res = post_json(f"{base}/moderate", {"text": "Hello friend, how are you?", "user_id": "u1"})
    print(f"Clean: {code} {res}")

    # Spam
    print("\nTesting /moderate (Spam)...")
    code, res = post_json(f"{base}/moderate", {"text": "BUY CRYPTO NOW SPAM SPAM SPAM", "user_id": "u2"})
    print(f"Spam: {code} {res}")

if __name__ == "__main__":
    test()
