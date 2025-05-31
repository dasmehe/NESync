from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import pyautogui as pag
import hid
import asyncio
import time
from threading import Thread, Event, Lock

app = FastAPI()

# Allow all CORS (adjust in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global config dict
config = {
    "a": "a",
    "b": "b",
    "select": "shift",
    "start": "enter",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}

wait_time = 0.01
wait_lock = Lock()

vid = 0x0810
pid = 0xE501
device = None
stop_event = Event()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for conn in list(self.active_connections):
            try:
                await conn.send_text(message)
            except Exception:
                self.disconnect(conn)

manager = ConnectionManager()

def handle_input(buttons):
    for button in buttons:
        key = config.get(button)
        if key:
            pag.press(key)

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
        print("Listening to NES controller...")

        while not stop_event.is_set():
            data = device.read(64)
            if data:
                buttons = parse(data)
                if buttons:
                    handle_input(buttons)
                    asyncio.run_coroutine_threadsafe(manager.broadcast(str(buttons)), loop)
            with wait_lock:
                sleep = wait_time
            time.sleep(sleep)
    except Exception as e:
        print("Controller error:", e)
    finally:
        if device:
            device.close()

thread = None
loop = asyncio.get_event_loop()

@app.get("/")
async def root():
    return {"message": "FastAPI NES controller ready"}

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
    global thread
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

@app.post("/config")
async def receive_config(data: dict):
    global config
    config.update(data)
    print("Updated config:", config)
    return {"status": "success", "data": config}
