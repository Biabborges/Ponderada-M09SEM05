
# Sincronização de Estoque

Esta ponderada tem o objetivo de monitorar e sincronizar o estoque de pedidos realizados nos mercados da Rappi. Sempre que um produto tem alteração de disponibilidade, o sistema notifica os entregadores via WebSocket e Telegram.

## Estrutura do Projeto

```
PONDERADA-M09SEM05
├── images                  
├── src
│   ├── services
│   │   ├── inventory-sync  
│   │   │   ├── __pycache__/   
│   │   │   ├── .gitkeep       
│   │   │   ├── inventory_sync.py  
│   │   │   ├── locustfile.py  
│   │   │   ├── README.md      
│   │   │   ├── requirements.txt  
│   ├── README.md              
```

## Como Rodar o Projeto

### Instalar dependências
Certifique-se de ter o **Python 3.8+** instalado e execute o seguinte comando:

```bash
pip install -r src/services/inventory-sync/requirements.txt
```

### Executar o serviço
Para iniciar o servidor FastAPI e WebSocket, utilize:

```bash
python -m uvicorn src.services.inventory-sync.inventory_sync:app --reload
```

- O servidor estará disponível em: **http://127.0.0.1:8000**
- Para testar o WebSocket: **ws://127.0.0.1:8000/ws/estoque**
- Para visualizar a documentação interativa do FastAPI: **http://127.0.0.1:8000/docs**