from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import hid
import time
import asyncio
from threading import Thread, Event, Lock
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS from all origins (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vid = 0x0810
pid = 0xE501

device = None
stop_event = Event()
wait_time = 0.01
wait_lock = Lock()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Client probably disconnected, mark to remove
                to_remove.append(connection)
        for conn in to_remove:
            self.active_connections.remove(conn)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Hello, your FastAPI app is live!"}

def parse(data):
    buttons = []
    if data[4] == 0:
        buttons.append("up")
    elif data[4] == 255:
        buttons.append("down")
    if data[3] == 0:
        buttons.append("left")
    elif data[3] == 255:
        buttons.append("right")
    btn = data[5]
    if btn & 0x20:
        buttons.append("a")
    if btn & 0x10:
        buttons.append("b")
    if data[6] & 0x20:
        buttons.append("start")
    if data[6] & 0x10:
        buttons.append("select")
    return buttons

def controller_loop(loop):
    global device, wait_time
    try:
        device = hid.device()
        device.open(vid, pid)
        device.set_nonblocking(True)
        print("Listening to NES controller input...")

        while not stop_event.is_set():
            data = device.read(64)
            if data:
                buttons = parse(data)
                # Schedule broadcast on the main event loop safely
                asyncio.run_coroutine_threadsafe(manager.broadcast(str(buttons)), loop)
            with wait_lock:
                sleep_time = wait_time
            time.sleep(sleep_time)
    except Exception as e:
        print(f"Error in controller loop: {e}")
    finally:
        if device:
            device.close()
        print("Controller loop stopped")

thread = None
loop = asyncio.get_event_loop()  # Get the main asyncio event loop here

@app.websocket("/ws/buttons")
async def websocket_endpoint(websocket: WebSocket):
    global wait_time
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                new_wait = float(msg)
                with wait_lock:
                    wait_time = new_wait
                await websocket.send_text(f"wait_time updated to {wait_time}")
            except ValueError:
                await websocket.send_text("invalid float received")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/start")
async def start_controller():
    global thread, stop_event, loop
    if thread and thread.is_alive():
        return {"status": "already running"}
    stop_event.clear()
    thread = Thread(target=controller_loop, args=(loop,), daemon=True)
    thread.start()
    return {"status": "started"}

@app.post("/stop")
async def stop_controller():
    stop_event.set()
    return {"status": "stopping"}
