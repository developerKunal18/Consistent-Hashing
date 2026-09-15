from bisect import bisect_left
from hashlib import sha256
from threading import RLock
from flask import Flask, jsonify, request

app = Flask(__name__)

class ConsistentHashRing:
    def __init__(self, replicas=100):
        self.replicas = replicas
        self.ring = {}
        self.positions = []
        self.nodes = set()
        self.lock = RLock()

    @staticmethod
    def _hash(value):
        return int.from_bytes(sha256(value.encode()).digest()[:8], "big")

    def _position(self, node, replica):
        return self._hash(f"{node}:{replica}")

    def _rebuild(self):
        self.positions = sorted(self.ring)

    def add_node(self, node):
        if not isinstance(node, str) or not node.strip():
            raise ValueError("node must be a non-empty string")
        with self.lock:
            if node in self.nodes:
                return False
            self.nodes.add(node)
            for replica in range(self.replicas):
                pos = self._position(node, replica)
                while pos in self.ring:
                    pos = (pos + 1) & ((1 << 64) - 1)
                self.ring[pos] = node
            self._rebuild()
            return True

    def remove_node(self, node):
        with self.lock:
            if node not in self.nodes:
                return False
            self.nodes.remove(node)
            for pos, owner in list(self.ring.items()):
                if owner == node:
                    del self.ring[pos]
            self._rebuild()
            return True

    def get_node(self, key):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty string")
        with self.lock:
            if not self.positions:
                return None
            pos = self._hash(key)
            i = bisect_left(self.positions, pos)
            if i == len(self.positions):
                i = 0
            return self.ring[self.positions[i]]

    def get_nodes(self):
        with self.lock:
            return sorted(self.nodes)

    def stats(self):
        with self.lock:
            return {"nodes": len(self.nodes), "virtual_nodes": len(self.positions), "replicas_per_node": self.replicas}

ring = ConsistentHashRing()
for node in ("node-1", "node-2", "node-3"):
    ring.add_node(node)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "consistent-hashing"})

@app.get("/api/nodes")
def list_nodes():
    return jsonify({"nodes": ring.get_nodes()})

@app.post("/api/nodes")
def add_node():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("node"), str) or not body["node"].strip():
        return jsonify({"error": "JSON body with non-empty string 'node' is required"}), 400
    node = body["node"].strip()
    added = ring.add_node(node)
    return jsonify({"node": node, "added": added, "nodes": ring.get_nodes()}), 201

@app.delete("/api/nodes/<node>")
def remove_node(node):
    if not ring.remove_node(node):
        return jsonify({"error": "node not found"}), 404
    return jsonify({"node": node, "removed": True, "nodes": ring.get_nodes()})

@app.get("/api/route/<key>")
def route_key(key):
    node = ring.get_node(key)
    if node is None:
        return jsonify({"error": "no nodes available"}), 503
    return jsonify({"key": key, "node": node})

@app.get("/api/stats")
def stats():
    return jsonify(ring.stats())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
