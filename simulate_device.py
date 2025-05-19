import requests
import time
import random

API_URL = "http://localhost:8000/devices"  # Your FastAPI endpoint
DEVICE_IDS = ["sensor01", "sensor02", "sensor03", "sensor04"]

def simulate_device(device_id):
    return {
        "device_id": device_id,
        "status": "online",
        "battery": round(random.uniform(40, 100), 2), # Random battery %
        "sensor": round(random.uniform(15, 60), 2) # Random sensor reading
    }

while True:
    for device_id in DEVICE_IDS:
        payload = simulate_device(device_id)
        try:
            r = requests.post(API_URL, json=payload)
            print(f"{device_id}: {r.status_code}, {r.json()}")
        except Exception as e:
            print(f"{device_id}: Error - {e}")
    time.sleep(10)  # send every 10 second
