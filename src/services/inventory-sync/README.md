# RNF2 - Real-Time Stock Monitoring  

This requirement implements stock synchronization according to the **non-functional requirement RNF2**. It ensures **fast updates and continuous monitoring** of stock levels, utilizing FastAPI and WebSockets for real-time communication.  

## Features  

- **Stock Synchronization**: Automatic updates of available product quantities.  
- **Real-Time Notifications**: Clients connected via WebSocket receive instant updates.  
- **Stock Query**: REST endpoint to check the available quantity of products.  
- **Event Logging**: Detailed logs of WebSocket connections and stock updates.  

## How to Run the Project  

1. **Start the server**:  

```bash
python -m uvicorn src.services.inventory-sync.inventory_sync:app --reload
```

The server will be available at `http://127.0.0.1:8000/`.  

## API Endpoints  

### 1. WebSocket - `/ws/stock`  

- Allows clients to connect and receive stock update notifications.  
- Notifications are sent automatically every 5 seconds.  

**Example of WebSocket connection using JavaScript:**  

```javascript
const socket = new WebSocket("ws://localhost:8000/ws/stock");

socket.onmessage = function(event) {
    console.log("Stock update:", event.data);
};
```

### 2. GET - `/stock`  

Returns the current quantity of **Product X**.  

**Example of an HTTP request:**  

```bash
curl -X 'GET' 'http://127.0.0.1:8000/stock' -H 'accept: application/json'
```

**Expected response:**  

```json
{
  "product": "Product X",
  "quantity": 12
}
```

## **Load Testing - Results and Insights**  

### Results
![Results](../../../diagrams/test-locust.jpg)


To ensure the API meets the continuous stock monitoring requirements, we conducted load testing using **Locust**. The goal was to evaluate the scalability, stability, and response time of the application under high demand.  

### **Positive Highlights**  
**High stability:** The test was conducted with 1,000 simultaneous users, and the failure rate remained at 0%, demonstrating that the system responds reliably under load.  

**Significant increase in throughput:** The API reached **7.2 requests per second (RPS)**, a notable improvement compared to previous tests.  

**Consistent response time for most requests:** The median response time remained at **3,000 ms**, ensuring a predictable time for the majority of requests.  

### **Areas for Improvement and Opportunities**  
**Latency optimization for high loads**  
Although most requests had an acceptable response time, some peaks were observed:  
- **95% of requests:** Completed within **114,000 ms**.  
- **99% of requests:** Completed within **125,000 ms**.  
- **Maximum recorded response time:** **131,234 ms**.  

Therefore, the test demonstrated that the API is **stable, reliable, and scalable up to a certain point**, handling **1,000 simultaneous users with zero failures**. Additionally, removing artificial delays resulted in a significant increase in processed requests per second. To further improve efficiency, we will analyze latency spikes, optimize concurrency management, and test WebSocket scalability in upcoming sprints.