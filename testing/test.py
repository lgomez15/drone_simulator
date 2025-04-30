import asyncio
import websockets
import json

async def connect_to_websocket():
    uri = "ws://localhost:8000/ws"  # Ajusta la URI según tu servidor WebSocket
    async with websockets.connect(uri) as websocket:
        print("Conectado al WebSocket")
        try:
            while True:
                data = await websocket.recv()
                print(json.loads(data))
        except websockets.ConnectionClosed:
            print("Conexión cerrada")

if __name__ == "__main__":
    asyncio.run(connect_to_websocket())