import requests

API_URL = "http://localhost:8000/devices"

devices = [
    {
        "device_id": "sensor-001",
        "status": "online",
        "battery": 95.2,
        "sensor": 22.8,
        "error_rate": 0.0,
        "last_error": None
    },
    {
        "device_id": "sensor-002",
        "status": "online",
        "battery": 13.6,
        "sensor": 23.1,
        "error_rate": 0.0,
        "last_error": None
    },
    {
        "device_id": "sensor-003",
        "status": "error",
        "battery": 80.7,
        "sensor": 21.9,
        "error_rate": 0.45,
        "last_error": "SENSOR_FAIL"
    },
    {
        "device_id": "sensor-004",
        "status": "offline",
        "battery": 56.4,
        "sensor": 0.0,
        "error_rate": 0.1,
        "last_error": "NO_RESPONSE"
    },
    {
        "device_id": "sensor-005",
        "status": "online",
        "battery": 65.3,
        "sensor": 24.2,
        "error_rate": 0.37,
        "last_error": "INTERMITTENT"
    }
]

for device in devices:
    r = requests.post(API_URL, json=device)
    print(r.json())
