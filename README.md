# NESync

A bootleg DS4Windows for NES controllers using FastAPI backend and Tauri frontend.

## Features

- Real-time NES controller input via HID
- FastAPI server with WebSocket to broadcast button presses
- Tauri-powered GUI for easy start/stop and latency control

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
