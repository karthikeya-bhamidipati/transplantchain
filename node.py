"""
node.py
A single TransplantChain network node exposed as a RESTful Flask service.
Supports transaction gossip, block broadcast, peer registration,
and Nakamoto longest-valid-chain fork resolution.
"""
import argparse
import requests
from flask import Flask, jsonify, request
from blockchain import TransplantBlockchain
from models import Block, Transaction

app = Flask(__name__)
blockchain = None
peers = set()
seen_tx_ids = set()


def broadcast(path, payload, exclude=None):
    """Best-effort gossip to all registered peers."""
    for peer in list(peers):
        if peer == exclude:
            continue
        try:
            requests.post(f"{peer}{path}", json=payload, timeout=2)
        except requests.exceptions.RequestException:
            pass


@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify({
        "length": len(blockchain.chain),
        "chain": [b.to_dict() for b in blockchain.chain],
    })


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify({
        "chain_height": len(blockchain.chain) - 1,
        "chain_tip_hash": blockchain.get_latest_block().hash,
        "mempool_size": len(blockchain.mempool),
        "active_organs": list(blockchain.validator.active_organs.keys()),
        "active_patients": list(blockchain.validator.active_patients.keys()),
        "allocations": blockchain.validator.allocations,
        "peers": list(peers),
    })


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    data = request.get_json()
    tx = Transaction.from_dict(data)

    if tx.tx_id in seen_tx_ids:
        return jsonify({"message": "Already seen, ignored."}), 200
    seen_tx_ids.add(tx.tx_id)

    success, message = blockchain.add_transaction(tx)
    if not success:
        return jsonify({"error": message}), 400

    broadcast("/transactions/new", tx.to_dict())
    return jsonify({"message": message, "tx_id": tx.tx_id}), 201


@app.route("/mine", methods=["POST"])
def mine():
    block, message = blockchain.mine_mempool()
    if block is None:
        return jsonify({"message": message, "mined": False}), 400

    broadcast("/blocks/receive", block.to_dict())
    return jsonify({
        "message": message,
        "mined": True,
        "block": block.to_dict(),
    }), 200


@app.route("/blocks/receive", methods=["POST"])
def receive_block():
    data = request.get_json()
    block = Block.from_dict(data)
    success, message = blockchain.try_append_block(block)
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    nodes = request.get_json().get("nodes", [])
    for node in nodes:
        clean_url = node.rstrip("/")
        peers.add(clean_url)
    return jsonify({"message": f"Added {len(nodes)} peers.", "total_peers": list(peers)}), 200


@app.route("/nodes/unregister", methods=["POST"])
def unregister_nodes():
    nodes = request.get_json().get("nodes", [])
    for node in nodes:
        peers.discard(node.rstrip("/"))
    return jsonify({"message": f"Removed {len(nodes)} peers.", "remaining_peers": list(peers)}), 200


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    """Nakamoto Consensus: queries all peers and adopts the longest valid chain."""
    longest_chain = None
    max_length = len(blockchain.chain)

    for peer in list(peers):
        try:
            resp = requests.get(f"{peer}/chain", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                length = data["length"]
                candidate_blocks = [Block.from_dict(b) for b in data["chain"]]
                if length > max_length:
                    ok, _ = TransplantBlockchain.is_valid_chain(candidate_blocks, blockchain.difficulty)
                    if ok:
                        max_length = length
                        longest_chain = candidate_blocks
        except requests.exceptions.RequestException:
            continue

    if longest_chain:
        blockchain.replace_chain(longest_chain)
        return jsonify({
            "message": "Chain replaced with longer valid chain.",
            "new_height": len(blockchain.chain) - 1,
            "tip_hash": blockchain.get_latest_block().hash,
        }), 200

    return jsonify({
        "message": "Current chain is authoritative.",
        "height": len(blockchain.chain) - 1,
        "tip_hash": blockchain.get_latest_block().hash,
    }), 200


def main():
    parser = argparse.ArgumentParser(description="TransplantChain P2P Node")
    parser.add_argument("--port", type=int, default=5000, help="Port to run node on")
    parser.add_argument("--difficulty", type=int, default=2, help="PoW difficulty target")
    args = parser.parse_args()

    global blockchain
    blockchain = TransplantBlockchain(difficulty=args.difficulty)
    print(f"TransplantChain node starting on port {args.port} (difficulty={args.difficulty})...")
    app.run(host="0.0.0.0", port=args.port, threaded=True)


if __name__ == "__main__":
    main()
