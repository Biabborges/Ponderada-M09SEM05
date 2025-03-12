from locust import HttpUser, task, between
import websocket
import threading
import time

class FastAPIUser(HttpUser):
    @task(2)
    def get_estoque(self):
        """Simula um usuário acessando a rota HTTP /estoque."""
        response = self.client.get("/estoque")
        if response.status_code == 200:
            print(f"Estoque atual: {response.json()}")

    @task(1)
    def connect_websocket(self):
        """Simula um usuário conectando ao WebSocket e escutando mensagens."""
        def on_message(ws, message):
            print(f"Mensagem recebida: {message}")

        def on_error(ws, error):
            print(f"Erro no WebSocket: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"Conexão WebSocket fechada: {close_msg}")

        def on_open(ws):
            print("Conectado ao WebSocket. Enviando mensagem de teste...")
            ws.send("Teste de conexão")
            time.sleep(10)
            ws.close()

        ws_url = f"ws://{self.host}/ws/estoque"
        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open

        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.start()
        ws_thread.join()
