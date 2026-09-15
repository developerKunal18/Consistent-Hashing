# Consistent Hashing

A Flask service demonstrating consistent hashing for distributing keys across nodes.

## Features

- Hash ring implementation
- Virtual nodes for better distribution
- Dynamic node addition/removal
- Stable key-to-node routing
- Thread-safe operations
- Ring statistics
- Health endpoint
- Pytest tests

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/nodes` | List nodes |
| POST | `/api/nodes` | Add a node |
| DELETE | `/api/nodes/<node>` | Remove a node |
| GET | `/api/route/<key>` | Find node for a key |
| GET | `/api/stats` | Ring statistics |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
pytest -q
```

## Example

```bash
curl http://localhost:5000/api/route/user-100
```

Add a node:

```bash
curl -X POST http://localhost:5000/api/nodes -H "Content-Type: application/json" -d '{"node":"node-4"}'
```

Remove a node:

```bash
curl -X DELETE http://localhost:5000/api/nodes/node-4
```

## Learning Goals

Learn hash rings, virtual nodes, distributed data placement, horizontal scaling, and the key ideas behind distributed caches and storage systems.
