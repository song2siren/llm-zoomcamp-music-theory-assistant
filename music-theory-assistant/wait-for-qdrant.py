# Simple readiness probe for Qdrant
import os, time
import urllib.request

url = os.getenv("QDRANT_URL", "http://qdrant:6333") + "/readyz"

for i in range(60):
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            if r.status == 200:
                print("Qdrant is ready.")
                break
    except Exception:
        pass
    print("Waiting for Qdrant...", i + 1)
    time.sleep(2)
else:
    raise SystemExit("Qdrant did not become ready in time.")
