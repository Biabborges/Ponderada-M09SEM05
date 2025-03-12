import asyncio
import random
import logging
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = "7540872198:AAHEM51CBhBV5DIbho7pZzo2lKKpaya3O0o"
TELEGRAM_CHAT_ID = "5871334021"

estoque = {"Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml": random.randint(5, 20)}

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

def enviar_mensagem_telegram(mensagem: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Mensagem enviada ao Telegram: {mensagem}")
        else:
            logging.error(f"Erro ao enviar mensagem ao Telegram: {response.text}")
    except Exception as e:
        logging.error(f"Falha na requisição ao Telegram: {e}")

async def monitorar_estoque():
    while True:
        try:
            estoque["Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml"] = random.randint(0, 20)  # Simulação de alteração de estoque
            atualizacao = f"📢 Atualização de estoque: Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml - {estoque['Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml']} unidades"

            await manager.broadcast(atualizacao)

            if estoque["Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml"] <= 5:
                enviar_mensagem_telegram(f"⚠️ Estoque baixo: Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml tem apenas {estoque['Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml']} unidades!")

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
    logging.info(f"Respondendo com estoque atual: {estoque['Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml']} unidades.")
    return {"produto": "Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml", "quantidade": estoque["Produto X"]}
