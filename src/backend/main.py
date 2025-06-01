from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import pyautogui as pag
import hid
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

vid = 0x0810
pid = 0xE501

stop_event = None
controller_task = None
wait_time = 0.01
wait_lock = asyncio.Lock()
executor = ThreadPoolExecutor(max_workers=1)
device = None

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        to_remove = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                to_remove.append(conn)
        for conn in to_remove:
            self.disconnect(conn)

manager = ConnectionManager()

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

def handle_input(buttons):
    for button in buttons:
        key = config.get(button)
        if key:
            pag.press(key)

async def read_device():
    global device
    return await asyncio.get_event_loop().run_in_executor(executor, device.read, 64)

async def controller_loop():
    global device, wait_time, stop_event
    try:
        device = hid.device()
        device.open(vid, pid)
        device.set_nonblocking(True)
        print("Listening to NES controller...")

        while not stop_event.is_set():
            data = await read_device()
            print("Raw read:", data)  # <-- NEW DEBUG LINE
            if data:
                buttons = parse(data)
                if buttons:
                    handle_input(buttons)
                    await manager.broadcast(str(buttons))
            async with wait_lock:
                sleep = wait_time
            await asyncio.sleep(sleep)
    except Exception as e:
        print("Controller error:", e)
    finally:
        if device:
            device.close()
        print("Controller loop stopped.")

@app.get("/")
async def root():
    return {"message": "FastAPI NES controller ready"}

@app.websocket("/ws/buttons")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                new_wait = float(msg)
                async with wait_lock:
                    global wait_time
                    wait_time = new_wait
                await websocket.send_text(f"wait_time updated to {wait_time}")
            except ValueError:
                await websocket.send_text("invalid float received")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/start")
async def start_controller():
    global controller_task, stop_event
    if controller_task and not controller_task.done():
        return {"status": "already running"}
    
    stop_event = asyncio.Event()
    controller_task = asyncio.create_task(controller_loop())
    return {"status": "started"}

@app.post("/stop")
async def stop_controller():
    global stop_event
    if stop_event:
        stop_event.set()
    if controller_task:
        await controller_task
    return {"status": "stopped"}

@app.post("/config")
async def receive_config(data: dict):
    global config
    config.update(data)
    print("Updated config:", config)
    return {"status": "success", "data": config}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
