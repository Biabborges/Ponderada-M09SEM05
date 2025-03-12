import asyncio
import random
import logging
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TELEGRAM_BOT_TOKEN = "7540872198:AAHEM51CBhBV5DIbho7pZzo2lKKpaya3O0o"
TELEGRAM_CHAT_ID = "5871334021"

produto_nome = "Vinho Chileno Tinto Seco Aves Del Sur Carménère Valle del Loncomilla Garrafa 750ml"
estoque = {produto_nome: random.randint(5, 20)}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info("Nova conexão WebSocket estabelecida.")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logging.info("Conexão WebSocket encerrada.")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"Erro ao enviar mensagem para um WebSocket: {e}")
                self.disconnect(connection)
        logging.info(f"Mensagem enviada para {len(self.active_connections)} conexões: {message}")


manager = ConnectionManager()


def enviar_mensagem_telegram(mensagem: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}

    for tentativa in range(3):
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logging.info(f"Mensagem enviada ao Telegram: {mensagem}")
                return
            else:
                logging.warning(f"Tentativa {tentativa + 1} falhou: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao conectar com Telegram: {e}")

    logging.error("Falha ao enviar mensagem após 3 tentativas.")


async def monitorar_estoque():
    while True:
        try:
            estoque[produto_nome] = random.randint(0, 20)
            atualizacao = f"📢 Atualização de estoque: {produto_nome} - {estoque[produto_nome]} unidades"

            await manager.broadcast(atualizacao)

            if estoque[produto_nome] <= 5:
                enviar_mensagem_telegram(
                    f"⚠️ Estoque baixo: {produto_nome} tem apenas {estoque[produto_nome]} unidades!"
                )

            logging.info(atualizacao)
        except KeyError as ke:
            logging.error(f"Erro ao acessar estoque: {ke}")
        except Exception as e:
            logging.error(f"Erro inesperado na sincronização do estoque: {e}")

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
            try:
                data = await websocket.receive_text()
                logging.info(f"Mensagem recebida via WebSocket: {data}")
                await websocket.send_text(f"Mensagem recebida: {data}")
            except Exception as e:
                logging.error(f"Erro ao processar mensagem do WebSocket: {e}")
                break
    except WebSocketDisconnect:
        logging.info("Cliente desconectado do WebSocket.")
    except Exception as e:
        logging.error(f"Erro inesperado no WebSocket: {e}")
    finally:
        manager.disconnect(websocket)


@app.get("/estoque")
async def get_estoque():
    try:
        logging.info("Recebida solicitação para consulta do estoque.")
        await asyncio.sleep(3)
        quantidade = estoque.get(produto_nome, "Produto não encontrado")
        logging.info(f"Respondendo com estoque atual: {quantidade} unidades.")
        return {"produto": produto_nome, "quantidade": quantidade}
    except Exception as e:
        logging.error(f"Erro ao consultar estoque: {e}")
        return {"erro": "Não foi possível obter o estoque no momento."}
