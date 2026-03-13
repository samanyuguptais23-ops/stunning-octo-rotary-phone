from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os
import aiofiles

from database import get_db, Message, SessionLocal

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

app = FastAPI(title="PulseLink API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

class MessageCreate(BaseModel):
    type: str = "general"
    priority: int = 4
    content: str = ""
    sender: str
    sender_name: str = "Anonymous"
    audio_url: str = ""

class MeshManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, device_id: str, ws: WebSocket):
        await ws.accept()
        self.active[device_id] = ws

    def disconnect(self, device_id: str):
        self.active.pop(device_id, None)

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        dead = []
        for device_id, ws in self.active.items():
            if device_id != exclude:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(device_id)
        for d in dead:
            self.active.pop(d, None)

mesh = MeshManager()

@app.websocket("/ws/{device_id}")
async def ws_endpoint(ws: WebSocket, device_id: str):
    await mesh.connect(device_id, ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        mesh.disconnect(device_id)

@app.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    msgs = db.query(Message).order_by(Message.priority, Message.created_at.desc()).limit(200).all()
    return [
        {
            "id": m.id,
            "type": m.type,
            "priority": m.priority,
            "content": m.content,
            "sender": m.sender,
            "sender_name": m.sender_name,
            "audio_url": m.audio_url,
            "created_at": m.created_at.isoformat()
        } for m in msgs
    ]

@app.post("/messages")
async def post_message(body: MessageCreate, db: Session = Depends(get_db)):
    msg = Message(
        id=str(uuid.uuid4()),
        type=body.type,
        priority=body.priority,
        content=body.content,
        sender=body.sender,
        sender_name=body.sender_name,
        audio_url=body.audio_url,
        created_at=datetime.utcnow()
    )
    db.add(msg)
    db.commit()

    payload = {
        "id": msg.id,
        "type": msg.type,
        "priority": msg.priority,
        "content": msg.content,
        "sender": msg.sender,
        "sender_name": msg.sender_name,
        "audio_url": msg.audio_url,
        "created_at": msg.created_at.isoformat()
    }
    await mesh.broadcast(payload)
    return {"status": "ok", "id": msg.id}

@app.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".m4a"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(MEDIA_DIR, filename)

    async with aiofiles.open(filepath, "wb") as out:
        content = await file.read()
        await out.write(content)

    return {"url": f"/media/{filename}"}