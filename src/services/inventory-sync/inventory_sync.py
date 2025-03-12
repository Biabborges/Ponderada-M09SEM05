import asyncio
import random
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

estoque = {"Produto X": random.randint(5, 20)}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info("Nova conexão WebSocket estabelecida.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logging.info("Conexão WebSocket encerrada.")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
        logging.info(f"Mensagem enviada para {len(self.active_connections)} conexões: {message}")

manager = ConnectionManager()

async def monitorar_estoque():
    while True:
        try:
            estoque["Produto X"] = random.randint(5, 20)
            atualizacao = f"Atualização de estoque: Produto X - {estoque['Produto X']} unidades"
            await manager.broadcast(atualizacao)
            logging.info(atualizacao)
        except Exception as e:
            logging.error(f"Erro na sincronização do estoque: {e}")
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Iniciando monitoramento do estoque...")
    background_task = asyncio.create_task(monitorar_estoque())
    yield
    background_task.cancel()
    logging.info("Encerrando monitoramento do estoque...")

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/estoque")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Mensagem recebida via WebSocket: {data}")
            await websocket.send_text(f"Mensagem recebida: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/estoque")
async def get_estoque():
    logging.info("Recebida solicitação para consulta do estoque.")
    await asyncio.sleep(3)
    logging.info(f"Respondendo com estoque atual: {estoque['Produto X']} unidades.")
    return {"produto": "Produto X", "quantidade": estoque["Produto X"]}
