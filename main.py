import os
import smtplib
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

# ---- Load environment variables ----
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST", "sandbox.smtp.mailtrap.io")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))

# ---- Enhanced email sending logic with HTML ----
def send_critical_email(device_id, issue, data=None):
    subject = f"ALERT: Device {device_id} Critical Event"
    html_body = f"""
    <html>
    <body style="font-family:Arial, sans-serif; color:#333;">
      <h2 style="color:#b30000;"> ALERT: Critical Event for Device: <span style='color:#0057b7'>{device_id}</span></h2>
      <p><b>Issue:</b> <span style="color:#d9534f">{issue}</span></p>
    """

    if data:
        html_body += f"""
        <h3>Device Details</h3>
        <table style="border-collapse:collapse;">
          <tr><td><b>Status:</b></td><td>{data.status}</td></tr>
          <tr><td><b>Battery:</b></td><td>{data.battery}</td></tr>
          <tr><td><b>Sensor:</b></td><td>{data.sensor}</td></tr>
          <tr><td><b>Error Rate:</b></td><td>{data.error_rate}</td></tr>
          <tr><td><b>Last Error:</b></td><td>{data.last_error}</td></tr>
        </table>
        """
    html_body += """
      <p style="margin-top:2em; color:#888;">This is an automated message from your IoT Device Monitoring System.</p>
    </body>
    </html>
    """

    # Build email headers
    message = f"Subject: {subject}\nContent-Type: text/html\n\n{html_body}"

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_USER, message)
        print(f"Enhanced email sent for {device_id} - {issue}")
    except Exception as e:
        print("Failed to send email:", e)

# ---- FastAPI and DB setup ----
app = FastAPI()
DATABASE_URL = "sqlite:///./devices.db"
engine = create_engine(DATABASE_URL, echo=True)

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(index=True, unique=True)
    status: str
    battery: float
    sensor: float
    error_rate: float = 0.0
    last_error: Optional[str] = None

class DeviceData(BaseModel):
    device_id: str
    status: str
    battery: float
    sensor: float
    error_rate: float = 0.0
    last_error: Optional[str] = None

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    return {"msg": "IoT Device Health API with Email Alerts"}

@app.post("/devices")
def update_device(
    data: DeviceData,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Check if device exists
    statement = select(Device).where(Device.device_id == data.device_id)
    device = session.exec(statement).first()
    if device:
        # Update existing device
        device.status = data.status
        device.battery = data.battery
        device.sensor = data.sensor
        device.error_rate = data.error_rate
        device.last_error = data.last_error
    else:
        device = Device(**data.dict())
        session.add(device)
    session.commit()
    session.refresh(device)

    # Trigger enhanced HTML email if critical event detected
    issue = None
    if data.status == "error":
        issue = "Error State"
    elif data.status == "offline":
        issue = "Device Offline"
    elif data.battery < 20:
        issue = "Battery Critically Low"
    if issue:
        background_tasks.add_task(send_critical_email, data.device_id, issue, data)

    return {"msg": f"Device {device.device_id} updated", "data": data.dict()}

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