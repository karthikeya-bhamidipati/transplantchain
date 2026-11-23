# TransplantChain: Architectural Deep-Dive & Component Reference Manual

---

## 1. Executive Summary & The Mental Model

### What is TransplantChain?
**TransplantChain** is a decentralized, application-specific blockchain protocol designed to solve a life-and-death governance crisis: **organ allocation corruption, VIP queue-jumping, arbitrary organ discards, and lack of transparency on deceased donor waitlists**.

In conventional organ transplant administration:
* Waitlists and allocations are managed on centralized relational databases (such as UNOS's UNet in the US or state registries under NOTTO in India).
* Centralized systems concentrate administrative authority in hospital transplant coordinators and database administrators. This structure creates vulnerabilities where bad actors can silently edit patient urgency tiers (e.g. MELD scores), manipulate waitlist queues to favor wealthy or politically connected VIP patients, or discard organs without transparent accountability.

In general-purpose public blockchains (such as Ethereum):
* Smart contracts provide immutability, but evaluating multi-factor clinical matching, blood compatibility, and cold-ischemia countdowns on thousands of patients incurs severe gas costs. Furthermore, general-purpose chains lack native domain safeguards against asynchronous race conditions where two surgeons attempt to claim the same donor organ simultaneously.

### The Core Technical Innovation
TransplantChain integrates a **Medical Allocation Gatekeeper** directly into the blockchain consensus and transaction validation engine.

* **Algorithmic Fairness Invariant (Anti-Queue-Jumping):** Every validating node independently computes deterministic medical priority scores (incorporating urgency/MELD score, waiting time, and HLA tissue compatibility). A block proposal is mathematically invalid if it contains an allocation to a lower-priority patient when a higher-priority eligible candidate exists.
* **Cold-Ischemia Viability Invariant:** Organs degrade outside the human body (heart: 4–6 hrs, liver: 12 hrs, kidney: 24 hrs). A transaction attempting to allocate or transplant an organ past its maximum cold-ischemic window is automatically rejected by the consensus engine, preventing dangerous clinical malpractice.
* **Consensus-Enforced Multi-Hospital Trust:** Competing hospital networks (Donor Hospitals, Recipient Transplant Centers, and Regulatory OPOs) run independent validating nodes. Nodes do not simply trust each other; they independently replay all medical and cryptographic rules from Genesis.

---

## 2. System Architecture & High-Level Flow

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    HOSPITAL / OPO / CLIENT LAYER                                    |
|  - Generates SECP256k1 Keypairs (Private/Public Keys for Hospitals and OPOs)                       |
|  - Submits REGISTER_ORGAN, REGISTER_PATIENT, or ALLOCATE_ORGAN Transactions                         |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
                                                  │
                                                  ▼
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                NODE LAYER: node.py (Flask HTTP P2P)                                 |
|  Endpoints: POST /transactions/new, POST /mine, GET /nodes/resolve, GET /state                     |
|  Gossip Protocol: Floods unseen transactions and newly mined blocks across peer hospital nodes      |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
                                                  │
                                                  ▼
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                       TRANSACTION VALIDATION PIPELINE: blockchain.py                               |
|                                                                                                    |
|  1. Cryptographic Verification (models.py)                                                         |
|     └── Verify SECP256k1 ECDSA signature over SHA-256 canonical transaction hash                   |
|                                                                                                    |
|  2. Medical Allocation Gatekeeper (validator.py)                                                   |
|     ├── ABO Compatibility Rule: Donor O (Universal), A, B, AB matching matrix                      |
|     ├── Cold-Ischemia Viability Rule: (Current Time - Harvest Time) <= Max Allowed Hours           |
|     └── Algorithmic Fairness Rule: Proposed candidate MUST have the highest priority score         |
|         Score = Urgency (MELD 6-40) + (0.01 * Waiting Days) + (1.5 * HLA Matches)                  |
|                                                                                                    |
|  3. State Verification & Uniqueness Check                                                          |
|     ├── Ensure organ is REGISTERED and currently AVAILABLE (prevents double-allocation)            |
|     └── Ensure patient is on WAITLIST and requires this exact organ type                           |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
         │ (Fails Any Check)                                          │ (Passes All Checks)
         ▼                                                            ▼
+───────────────────────────+                               +────────────────────────────────────────+
|   REJECTED IMMEDIATELY    |                               |           MEMPOOL ADMISSION            |
| "Fairness Violation:      |                               | Queued for inclusion into next block;  |
|  Queue-Jumping Detected"  |                               | gossiped to all network hospital peers |
+───────────────────────────+                               +────────────────────────────────────────+
                                                                      │
                                                                      ▼
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    CONSENSUS & MINING ENGINE                                       |
|  - Batch Assembly: Sequentially re-checks mempool transactions to drop sibling double-claims       |
|  - Merkle Tree Construction: Computes binary SHA-256 Merkle Root                                    |
|  - Proof-of-Work (PoW): Searches for nonce satisfying hash.startswith("0" * difficulty)            |
|  - Chain Extension: Commits block, updates organ status to ALLOCATED, patient to TRANSPLANTED      |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
                                                  │
                                                  ▼
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                             MULTI-NODE CONSENSUS & FORK RESOLUTION                                 |
|  - Nakamoto Consensus: Longest-valid-chain rule resolves network partitions                        |
|  - State Replay: Receiving node independently re-verifies all medical rules from Genesis Block #0   |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Component-by-Component Walkthrough

The codebase is organized into clean, modular files with clear responsibilities:

```
transplantchain/
├── models.py                  # Cryptographic models (Transaction, Block, MerkleTree, ECDSA)
├── validator.py               # Medical Gatekeeper (ABO compatibility, ischemia countdown, fairness)
├── blockchain.py              # State machine, mempool, PoW mining, consensus, chain replay
├── synthetic_data.py          # Realistic clinical data generator (patients, organs, HLA profiles)
├── node.py                    # Multi-node HTTP peer-to-peer daemon (Flask)
├── run_network_demo.py        # Automated 3-node P2P partition & fork resolution demonstration
├── benchmark.py               # Empirical benchmarking suite (matching latency, PoW scaling)
├── demo_correctness_fixes.py  # Adversarial test suite (queue-jumping, expired organs, sibling claims)
├── app.py                     # Streamlit web dashboard (visual inventory, live attack simulation)
├── make_diagrams.py           # Programmatic architecture diagram generator
├── diagrams/                  # Generated high-resolution architecture diagrams (.png)
├── results/                   # Benchmark CSVs and generated plots (.png)
└── requirements.txt           # Python dependency specifications
```

---

### File 1: `models.py` (Data Structures & Cryptography)

**Purpose:** Defines the core data primitives and cryptographic functions that ensure transactions and blocks are authentic, tamper-evident, and serializable across network nodes.

#### Key Classes:

#### 1. `Transaction`
Represents an atomic medical event:
* `tx_type`: 
  * `"REGISTER_ORGAN"`: Harvested organ logged by an Organ Procurement Organization (OPO).
  * `"REGISTER_PATIENT"`: Critically ill patient waitlisted by a hospital.
  * `"ALLOCATE_ORGAN"`: Organ assigned to the highest-priority eligible candidate.
* `sender_pubkey`: Hex-encoded SECP256k1 public key of the hospital or surgeon.
* `payload`: Structured dictionary holding medical parameters (blood type, HLA antigens, MELD score, harvest time, etc.).
* `calculate_hash()`: Deterministic SHA-256 over alphabetically sorted JSON (`sort_keys=True`).
* `sign_transaction(private_key_hex)`: Cryptographically signs `tx_id` using the **SECP256k1** elliptic curve.
* `verify_signature()`: Validates that the payload was authentically signed by `sender_pubkey`.
* `to_dict()` and `from_dict()`: Enables lossless network serialization over HTTP without altering transaction hashes.

#### 2. `MerkleTree`
* `compute_root(transactions)`: Computes a balanced binary SHA-256 Merkle root. Any modification to an individual transaction invalidates the Merkle root and breaks the block header.

#### 3. `Block`
* Represents a mined batch of transactions containing `index`, `timestamp`, `previous_hash`, `merkle_root`, `difficulty`, `nonce`, and `hash`.
* `mine_block()`: Proof-of-Work search loop satisfying the target difficulty (`hash.startswith("0" * difficulty)`).
* `is_valid()`: Re-computes Merkle root, verifies PoW hash target, and verifies all transaction signatures.

---

### File 2: `validator.py` (The Medical Allocation Gatekeeper)

**Purpose:** Enforces clinical compatibility and mathematical fairness rules at the protocol level.

#### Key Functions & Classes:

* **`BLOOD_COMPATIBILITY`**: The standard medical ABO blood matrix:
  * Donor O $\rightarrow$ Recipients O, A, B, AB (Universal Donor)
  * Donor A $\rightarrow$ Recipients A, AB
  * Donor B $\rightarrow$ Recipients B, AB
  * Donor AB $\rightarrow$ Recipient AB (Universal Recipient)
* **`DEFAULT_ISCHEMIA_LIMITS`**: Clinically accepted maximum cold-ischemia windows:
  * Heart: 4.0 hours
  * Lung: 6.0 hours
  * Liver: 12.0 hours
  * Kidney: 24.0 hours
* **`compute_priority_score(urgency_score, waiting_time_days, hla_matches)`**:
  $$\text{Score} = \text{Urgency (MELD 6–40)} + (0.01 \times \text{Waiting Days}) + (1.5 \times \text{HLA Matches})$$
* **`MedicalAllocationValidator`**:
  * Tracks `active_organs`, `active_patients`, and `allocations`.
  * `get_eligible_candidates(organ)`: Filters waitlisted patients by organ type and ABO compatibility, computes priority scores, and ranks candidates in descending order.
  * `validate_allocation(organ_id, patient_id, allocation_time)`:
    1. Verifies organ exists and is currently `AVAILABLE`.
    2. Verifies patient exists and is currently `WAITLISTED`.
    3. Verifies organ type matches what the patient needs.
    4. Enforces ABO blood compatibility.
    5. Enforces cold-ischemia viability:
       $$\frac{\text{Current Time} - \text{Harvest Time}}{3600} \le \text{Max Ischemia Hours}$$
    6. **Algorithmic Fairness Check (Anti-Queue-Jumping):** Compares proposed patient's score against the top-ranked candidate. If a patient with a higher score was bypassed, returns:
       `Fairness Violation (Queue-Jumping Detected): Proposed patient bypassed higher-priority candidate.`
  * `apply_allocation(organ_id, patient_id)`: Transitions organ to `ALLOCATED` and patient to `TRANSPLANTED`.

---

### File 3: `blockchain.py` (Consensus & State Machine)

**Purpose:** Connects cryptography, medical validation, and peer consensus into an immutable ledger.

#### Key Functions & Classes:
* **`clone_validator(validator)`**: Creates a deep copy of validator state for isolated tentative validation before mempool admission.
* **`apply_transaction(tx, validator)`**: The **Single Source of Truth** for state transitions. Used across mempool admission, block assembly, peer block reception, and chain replay.
* **`TransplantBlockchain`**:
  * `create_genesis_block()`: Seeds Block #0 with `GENESIS_ORGAN`.
  * `add_transaction()`: Clones state, validates transaction, and enqueues into mempool.
  * `mine_mempool()`: **Sibling-Conflict Resolution:** Re-evaluates mempool transactions sequentially. If two doctors submitted competing claims for the same organ before mining, the first claim is confirmed into the block and the conflicting second claim is safely dropped.
  * `try_append_block()`: Replays all transactions in an incoming peer block against a local validator clone before extending the chain tip.
  * `is_valid_chain()`: Fully re-derives a candidate chain from Genesis Block #0, re-executing all medical rules.
  * `replace_chain()`: Nakamoto consensus: adopts longer valid chain and prunes confirmed mempool transactions.

---

### File 4: `synthetic_data.py` (Clinical Dataset Generator)

**Purpose:** Generates realistic, diverse clinical test datasets:
* 6 detailed patients across Kidney, Liver, and Heart requirements with varied MELD scores (19.5 to 39.8), blood types, and HLA antigen pools.
* 4 donor organs with varying harvest times, including:
  * Freshly harvested viable organs.
  * An organ harvested 30 hours ago (`DONOR-KIDNEY-EXPIRED`) specifically designed to demonstrate rejection of expired organs.
* `seed_blockchain(bc, priv, pub)`: Utility function that automatically populates a fresh blockchain instance for demonstration.

---

### File 5: `node.py` (HTTP Peer-to-Peer Daemon)

**Purpose:** Turns `TransplantBlockchain` into an independent RESTful network node using Flask:
* `POST /transactions/new`: Validates transaction and floods it to all registered peer nodes.
* `POST /mine`: Triggers local PoW mining and broadcasts the newly mined block.
* `POST /blocks/receive`: Receives a peer block and verifies it via `try_append_block()`.
* `POST /nodes/register` and `POST /nodes/unregister`: Dynamically adjusts network topology.
* `GET /nodes/resolve`: Triggers Nakamoto fork resolution by polling peers for the longest valid chain.

---

### File 6: `run_network_demo.py` (Distributed Network Demonstration)

**Purpose:** Automated end-to-end multi-process distributed network script:
1. Spawns 3 independent node processes:
   * Node A: Donor Hospital (Port 5000)
   * Node B: Recipient Hospital (Port 5001)
   * Node C: Regulatory OPO (Port 5002)
2. Connects them into a full mesh.
3. Tests transaction gossip (verifies unmined transactions propagate to B & C).
4. Tests block mining and propagation across all nodes.
5. Simulates a network partition isolating Node C.
6. Executes concurrent divergent mining: Node C mines 1 block (Height 2) while Nodes A and B mine 2 blocks together (Height 3).
7. Restores network connectivity, invokes `/nodes/resolve` on Node C, and verifies that Node C discards its shorter fork and reorganizes to the longer chain.

---

### File 7: `benchmark.py` (Empirical Benchmarking Suite)

**Purpose:** Measures real, reproducible quantitative performance and saves figures to `results/`:
1. **Experiment 1 (Matching Latency vs. Waitlist Size):** Evaluates candidate search time across waitlists from 10 to 5,000 patients. Confirms that indexed matching operates in sub-millisecond time.
2. **Experiment 2 (Proof-of-Work Scaling):** Evaluates mining latency across difficulty levels 1 to 5, proving empirical adherence to the theoretical $16^k$ exponential curve.

---

### File 8: `demo_correctness_fixes.py` (Adversarial Security Suite)

**Purpose:** Demonstrates protocol robustness against 4 critical attacks:
1. **VIP Queue-Jumping:** Bypassing a critical patient (MELD 38.5) to allocate to a VIP (MELD 22.0) $\rightarrow$ **REJECTED with `Fairness Violation`**.
2. **Expired Organ:** Allocating an organ harvested 30 hours ago $\rightarrow$ **REJECTED with `Clinical Viability Error`**.
3. **Sibling-Mempool Double-Claim:** Two concurrent allocation transactions for the same organ $\rightarrow$ **RESOLVED: First is mined, second dropped**.
4. **ABO Incompatibility:** Allocating Blood A organ to Blood B patient $\rightarrow$ **REJECTED with `ABO Incompatibility`**.

---

### File 9: `app.py` (Interactive Streamlit Dashboard)

**Purpose:** Human-in-the-loop web interface displaying:
* Live donor organ inventory with cold-ischemia countdown progress bars.
* Transparent patient waitlist with real-time algorithmic ranking.
* Interactive allocation portal with tabs for legitimate matching, custom registrations, and live attack simulations.
* Proof-of-Work mining button.
* Expandable blockchain ledger and Merkle root explorer.

---

## 4. Quick Verification Cheat Sheet for Viva & Demonstration

Run these commands in separate terminals during your evaluation:

### 1. Interactive Visual Demo (Streamlit)
```bash
streamlit run app.py
```
* **Fair Allocation:** Go to *Fair Medical Allocation* $\rightarrow$ Select organ $\rightarrow$ Click *Submit Legitimate Allocation to Mempool* $\rightarrow$ Click *Mine Pending Transactions*.
* **VIP Attack:** Go to *Attack Demonstration* $\rightarrow$ Click *Execute Queue-Jumping Attack* $\rightarrow$ Observe instant red rejection box.
* **Expired Organ Attack:** Select *Clinically Expired Organ Allocation* $\rightarrow$ Click *Execute Expired Organ Attack* $\rightarrow$ Observe viability error.

### 2. Multi-Node Distributed Network Demo
```bash
python run_network_demo.py
```
* Demonstrates multi-process mesh networking, gossip, partition, and fork resolution in $\approx 15\text{ seconds}$.

### 3. Adversarial Edge-Case Tests
```bash
python demo_correctness_fixes.py
```
* Programmatic proof that all 4 attack vectors are caught and rejected.

### 4. Empirical Benchmarks
```bash
python benchmark.py
```
* Re-runs empirical latency measurements and updates plots in `results/`.
