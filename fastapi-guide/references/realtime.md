# WebSockets and Streaming

## Basic WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

## WebSocket with Path Parameters

```python
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    await websocket.send_json({"msg": f"Welcome {client_id}"})
    try:
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({
                "client_id": client_id,
                "message": message
            })
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

## Connection Manager (Chat/Broadcast)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

## WebSocket Methods

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Receive
    text_data = await websocket.receive_text()
    json_data = await websocket.receive_json()
    bytes_data = await websocket.receive_bytes()

    # Send
    await websocket.send_text("Hello")
    await websocket.send_json({"msg": "Hello"})
    await websocket.send_bytes(b"bytes data")

    # Close
    await websocket.close()
```

## Streaming Response

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def generate_data():
    for i in range(10):
        yield f"data: Item {i}\n\n"
        await asyncio.sleep(0.5)

@app.get("/stream")
async def stream_data():
    return StreamingResponse(
        generate_data(),
        media_type="text/event-stream"
    )
```

## Server-Sent Events (SSE)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def event_generator():
    while True:
        # Simulate data updates
        data = {"time": str(datetime.now()), "value": random.randint(1, 100)}
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@app.get("/events")
async def get_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

## File Streaming

```python
from fastapi.responses import StreamingResponse

def iterfile(file_path: str):
    with open(file_path, "rb") as f:
        yield from f

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = f"files/{file_name}"
    return StreamingResponse(
        iterfile(file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )
```

## Large File Upload with Streaming

```python
from fastapi import UploadFile
import aiofiles

@app.post("/upload-large/")
async def upload_large_file(file: UploadFile):
    async with aiofiles.open(f"uploads/{file.filename}", "wb") as out_file:
        while content := await file.read(1024 * 1024):  # 1MB chunks
            await out_file.write(content)
    return {"filename": file.filename}
```

## Response Types

```python
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    FileResponse,
    StreamingResponse,
    JSONResponse
)

@app.get("/html/", response_class=HTMLResponse)
async def get_html():
    return "<html><body><h1>Hello</h1></body></html>"

@app.get("/text/", response_class=PlainTextResponse)
async def get_text():
    return "Hello, World!"

@app.get("/redirect/")
async def redirect():
    return RedirectResponse(url="/html/")

@app.get("/file/")
async def get_file():
    return FileResponse(
        "document.pdf",
        media_type="application/pdf",
        filename="downloaded_file.pdf"
    )
```
