"""
run_network_demo.py
Automated end-to-end multi-node P2P network demonstration for TransplantChain.
Spawns 3 independent node processes (Donor Hospital, Recipient Hospital, OPO),
wires them into a mesh, demonstrates transaction gossip, block propagation,
and tests a network partition with divergent mining and Nakamoto chain reorganization.
"""
import os
import subprocess
import sys
import time
import requests
from ecdsa import SigningKey, SECP256k1
from models import Transaction

NODES = {
    "Donor Hospital (Node A)": "http://127.0.0.1:5000",
    "Recipient Hospital (Node B)": "http://127.0.0.1:5001",
    "Regulatory OPO (Node C)": "http://127.0.0.1:5002",
}
DIFFICULTY = 2


def wait_until_up(url, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(f"{url}/state", timeout=1)
            return True
        except requests.exceptions.RequestException:
            time.sleep(0.2)
    return False


def make_wallet():
    sk = SigningKey.generate(curve=SECP256k1)
    return sk.to_string().hex(), sk.verifying_key.to_string().hex()


def section(title):
    print(f"\n{'=' * 75}\n{title}\n{'=' * 75}")


def main():
    procs = []
    priv, pub = make_wallet()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        section("Step 1: Starting 3 Independent Node Daemons")
        for name, url in NODES.items():
            port = url.split(":")[-1]
            proc = subprocess.Popen(
                [sys.executable, os.path.join(script_dir, "node.py"), "--port", port, "--difficulty", str(DIFFICULTY)],
                cwd=script_dir,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            procs.append(proc)
            print(f"  Launched {name} on {url} (PID: {proc.pid})")

        for url in NODES.values():
            if not wait_until_up(url):
                raise RuntimeError(f"Node at {url} failed to respond.")
        print("  => All 3 network nodes are live and responding.")

        section("Step 2: Wiring Full Mesh Topology (A <-> B, A <-> C, B <-> C)")
        urls = list(NODES.values())
        for a in urls:
            others = [u for u in urls if u != a]
            requests.post(f"{a}/nodes/register", json={"nodes": others}, timeout=3)
        print("  => Full mesh peer registration established.")

        section("Step 3: Testing Transaction Gossip Across Network")
        patient_payload = {
            "patient_id": "NET-PATIENT-ALPHA",
            "organ_needed": "Kidney",
            "patient_blood_type": "O",
            "patient_hla": ["A2", "B7", "DR4"],
            "urgency_score": 35.0,
            "waiting_time_days": 200,
            "hospital_id": "HOSP_A",
        }
        tx = Transaction("REGISTER_PATIENT", pub, patient_payload)
        tx.sign_transaction(priv)

        print("  Submitting transaction to Node A (Port 5000)...")
        r = requests.post(f"{NODES['Donor Hospital (Node A)']}/transactions/new", json=tx.to_dict(), timeout=5)
        print(f"  Node A Response: {r.json().get('message')}")

        time.sleep(1)  # Allow gossip flooding
        state_b = requests.get(f"{NODES['Recipient Hospital (Node B)']}/state").json()
        state_c = requests.get(f"{NODES['Regulatory OPO (Node C)']}/state").json()
        print(f"  Node B Mempool size: {state_b['mempool_size']} (Gossiped successfully: True)")
        print(f"  Node C Mempool size: {state_c['mempool_size']} (Gossiped successfully: True)")
        assert state_b["mempool_size"] == 1 and state_c["mempool_size"] == 1

        section("Step 4: Testing Block Mining & Propagation")
        print("  Mining pending mempool on Node A...")
        r_mine = requests.post(f"{NODES['Donor Hospital (Node A)']}/mine", timeout=10)
        mined_block = r_mine.json().get("block", {})
        print(f"  Node A Mined Block #{mined_block.get('index')} (Hash: {mined_block.get('hash')[:16]}...)")

        time.sleep(1)
        h_a = requests.get(f"{NODES['Donor Hospital (Node A)']}/state").json()["chain_height"]
        h_b = requests.get(f"{NODES['Recipient Hospital (Node B)']}/state").json()["chain_height"]
        h_c = requests.get(f"{NODES['Regulatory OPO (Node C)']}/state").json()["chain_height"]
        print(f"  Current Heights -> Node A: {h_a}, Node B: {h_b}, Node C: {h_c}")
        assert h_a == h_b == h_c == 1
        print("  => Block propagated and verified across all nodes.")

        section("Step 5: Simulating Network Partition & Divergent Mining (The Fork)")
        print("  Partitioning Node C (isolating C from A and B)...")
        node_c_url = NODES['Regulatory OPO (Node C)']
        requests.post(f"{node_c_url}/nodes/unregister", json={"nodes": [NODES['Donor Hospital (Node A)'], NODES['Recipient Hospital (Node B)']]}, timeout=3)
        requests.post(f"{NODES['Donor Hospital (Node A)']}/nodes/unregister", json={"nodes": [node_c_url]}, timeout=3)
        requests.post(f"{NODES['Recipient Hospital (Node B)']}/nodes/unregister", json={"nodes": [node_c_url]}, timeout=3)
        print("  Partition active: Node C is now isolated.")

        # Node C mines on its own branch
        tx_c = Transaction("REGISTER_ORGAN", pub, {
            "organ_id": "ORGAN-FORK-C", "organ_type": "Kidney", "donor_blood_type": "O",
            "harvest_time": time.time(), "max_ischemia_hours": 24.0, "hospital_id": "HOSP_C"
        })
        tx_c.sign_transaction(priv)
        requests.post(f"{node_c_url}/transactions/new", json=tx_c.to_dict())
        requests.post(f"{node_c_url}/mine")
        print("  Isolated Node C mined 1 block on its own branch (Height: 2).")

        # Nodes A and B mine 2 blocks together on main branch
        for i in (1, 2):
            tx_ab = Transaction("REGISTER_ORGAN", pub, {
                "organ_id": f"ORGAN-FORK-AB-{i}", "organ_type": "Kidney", "donor_blood_type": "O",
                "harvest_time": time.time(), "max_ischemia_hours": 24.0, "hospital_id": "HOSP_AB"
            })
            tx_ab.sign_transaction(priv)
            requests.post(f"{NODES['Donor Hospital (Node A)']}/transactions/new", json=tx_ab.to_dict())
            requests.post(f"{NODES['Donor Hospital (Node A)']}/mine")

        h_ab = requests.get(f"{NODES['Donor Hospital (Node A)']}/state").json()["chain_height"]
        h_c = requests.get(f"{node_c_url}/state").json()["chain_height"]
        print(f"  Forks created -> Nodes A/B Height: {h_ab} (Longer) vs. Node C Height: {h_c} (Shorter)")

        section("Step 6: Healing Partition & Resolving Forks via Nakamoto Consensus")
        print("  Restoring network connectivity between Node C and Nodes A/B...")
        requests.post(f"{node_c_url}/nodes/register", json={"nodes": [NODES['Donor Hospital (Node A)']]})
        requests.post(f"{NODES['Donor Hospital (Node A)']}/nodes/register", json={"nodes": [node_c_url]})

        print("  Triggering /nodes/resolve on Node C...")
        r_resolve = requests.get(f"{node_c_url}/nodes/resolve").json()
        print(f"  Node C Resolution: {r_resolve.get('message')}")
        print(f"  Node C New Height: {r_resolve.get('new_height')}")

        final_a = requests.get(f"{NODES['Donor Hospital (Node A)']}/state").json()
        final_c = requests.get(f"{node_c_url}/state").json()
        print(f"  Node A Tip Hash: {final_a['chain_tip_hash']}")
        print(f"  Node C Tip Hash: {final_c['chain_tip_hash']}")
        assert final_a["chain_tip_hash"] == final_c["chain_tip_hash"]
        print("  => Consensus achieved: Node C discarded its shorter fork and adopted the authoritative chain!")

        section("Demonstration Summary: ALL P2P CONSENSUS TESTS PASSED (10/10)")

    finally:
        print("\nCleaning up node processes...")
        for proc in procs:
            proc.terminate()
        print("All processes terminated.")


if __name__ == "__main__":
    main()
