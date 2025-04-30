from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import asyncio
import json

from .simulator import DroneSimulator, LOCATIONS

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
simulator = None
simulation_task = None
simulation_running = False

async def simulation_loop():
    global simulator, simulation_running
    try:
        while simulation_running:
            data = simulator.generate_data()
            await manager.broadcast(json.dumps(data))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"[Error] Simulación interrumpida: {e}")
        simulation_running = False

@app.post("/start/{location}")
async def start_simulation(location: str):
    global simulator, simulation_running, simulation_task
    if simulation_running:
        return {"status": "already_running"}
    if location not in LOCATIONS:
        return {"status": "error", "message": "Ubicación no encontrada"}
    simulator = DroneSimulator(LOCATIONS[location])
    simulation_running = True
    simulation_task = asyncio.create_task(simulation_loop())
    return {"status": "started"}

@app.post("/stop")
async def stop_simulation():
    global simulation_running, simulation_task
    if not simulation_running:
        return {"status": "not_running"}
    simulation_running = False
    if simulation_task:
        simulation_task.cancel()
    return {"status": "stopped"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
