# Network Route Optimization API

A FastAPI backend for a network route optimization take-home assignment.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the tests:
   ```bash
   pytest -v
   ```
4. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints

- POST /nodes
- GET /nodes
- DELETE /nodes/{id}
- POST /edges
- GET /edges
- DELETE /edges/{id}
- POST /routes/shortest
- GET /routes/history

## Curl walkthrough

```bash
curl -X POST http://127.0.0.1:8000/nodes -H "Content-Type: application/json" -d '{"name":"ServerA"}'
curl -X POST http://127.0.0.1:8000/nodes -H "Content-Type: application/json" -d '{"name":"ServerB"}'
curl -X POST http://127.0.0.1:8000/edges -H "Content-Type: application/json" -d '{"source":"ServerA","destination":"ServerB","latency":12.5}'
curl -X POST http://127.0.0.1:8000/routes/shortest -H "Content-Type: application/json" -d '{"source":"ServerA","destination":"ServerB"}'
curl http://127.0.0.1:8000/routes/history
```

## Design notes

- The graph is directed because a route from A to B does not imply the reverse route is valid or has the same latency.
- Adjacency is rebuilt for each query to keep the implementation simple and easy to reason about. This is a good tradeoff for a small assignment and can be optimized later with caching if needed.
- Validation ensures node names are present, edges are directed and positive, duplicates are rejected, and route requests only use existing nodes.
