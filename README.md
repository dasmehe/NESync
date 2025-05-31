# NES Controller API

A FastAPI backend to read NES controller input, map buttons to keyboard keys, and send input events to your system using `pyautogui`. Supports realtime config updates and websocket communication.

---

## Features

- Reads NES controller input via `hid`
- Maps buttons to custom keyboard keys (configurable)
- Sends keypress events to OS using `pyautogui`
- Websocket endpoint to update polling wait time dynamically
- REST endpoint to update button key mappings (config)
- Start/stop controller input loop via REST API
- CORS enabled for frontend integration

---

## Requirements

- Python 3.8+
- FastAPI
- uvicorn
- hidapi (via `hidapi` Python package)
- pyautogui
- asyncio

Install dependencies:

```bash
pip install fastapi uvicorn hidapi pyautogui
