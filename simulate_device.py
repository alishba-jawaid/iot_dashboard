import requests
import time
import random

API_URL = "http://localhost:8000/devices"
device_id = "sensor01"
error_codes = [None, "SENSOR_FAIL", "BATTERY_LOW", "OVERHEAT", "COMM_ERROR"]

while True:
    # Randomly decide if this report is an error
    is_error = random.random() < 0.1  # 10% chance of error
    status = "error" if is_error else "online"
    last_error = random.choice(error_codes) if is_error else None
    error_rate = round(random.uniform(0, 0.5), 2) if is_error else 0.0

    payload = {
        "device_id": device_id,
        "status": status,
        "battery": round(random.uniform(30, 100), 2),
        "sensor": round(random.uniform(10, 50), 2),
        "error_rate": error_rate,
        "last_error": last_error,
    }
    try:
        r = requests.post(API_URL, json=payload)
        print(f"Sent: {payload} | Server responded: {r.status_code} {r.json()}")
    except Exception as e:
        print("Error sending update:", e)
    time.sleep(10)