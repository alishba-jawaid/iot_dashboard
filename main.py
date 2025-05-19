from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory 'database' for now (we'll use a real one later)
devices: Dict[str, Dict] = {}

class DeviceData(BaseModel):
    device_id: str
    status: str  # "online" or "offline"
    battery: float
    sensor: float

@app.get("/")
def read_root():
    return {"msg": "IoT Device Health API is running"}

@app.post("/devices")
def update_device(data: DeviceData):
    devices[data.device_id] = data.dict()
    return {"msg": f"Device {data.device_id} updated", "data": data.dict()}

@app.get("/devices")
def get_devices():
    return list(devices.values())

@app.get("/devices/{device_id}")
def get_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]
