from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

# SQLite database file
DATABASE_URL = "sqlite:///./devices.db"
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL in console

# Device Table Definition
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True, unique=True)
    status: str
    battery: float
    sensor: float

# Device schema for API input
class DeviceData(BaseModel):
    device_id: str
    status: str
    battery: float
    sensor: float

# Create tables if not exist
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Dependency: get DB session
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    return {"msg": "IoT Device Health API with DB"}

@app.post("/devices")
def update_device(data: DeviceData, session: Session = Depends(get_session)):
    # Check if device exists
    statement = select(Device).where(Device.device_id == data.device_id)
    device = session.exec(statement).first()
    if device:
        # Update existing device
        device.status = data.status
        device.battery = data.battery
        device.sensor = data.sensor
    else:
        # Create new device
        device = Device(**data.dict())
        session.add(device)
    session.commit()
    session.refresh(device)
    return {"msg": f"Device {device.device_id} updated", "data": device}

@app.get("/devices", response_model=List[Device])
def get_devices(session: Session = Depends(get_session)):
    statement = select(Device)
    devices = session.exec(statement).all()
    return devices

@app.get("/devices/{device_id}", response_model=Device)
def get_device(device_id: str, session: Session = Depends(get_session)):
    statement = select(Device).where(Device.device_id == device_id)
    device = session.exec(statement).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
