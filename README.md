# TransplantChain: A Decentralized Organ Allocation & Cold-Ischemia Protocol

A custom Python blockchain that embeds **deterministic medical fairness (anti-queue-jumping)** and **cold-ischemia viability verification** into transaction and block validation, applied to organ transplantation waitlists.

An organ allocation transaction is only permitted into a block if the proposed recipient possesses the strictly highest deterministic medical priority score among all eligible candidates, and if the organ has not exceeded its clinical cold-ischemic viability window.

---

## Primary Submission & Academic Documents

| File | Purpose |
|---|---|
| **`FINAL_BLOCKCHAIN_PROJECT_REPORT.docx`** | **Official Moodle Submission Report** (Formatted Microsoft Word document with embedded high-resolution diagrams, benchmark plots, styled tables, and academic citations) |
| **`MENTOR_PRESENTATION_NOTES.docx`** | **Mentor Presentation & Defense Notes** (Formatted Word document with the 60-second pitch, pipeline, deep code walkthrough, live demo script, and top 10 viva defense Q&A) |
| **`FINAL_PROJECT_REPORT.md`** | Academic submission report in GitHub Flavored Markdown mapped directly to the 30-mark evaluation rubric |
| **`MENTOR_PRESENTATION_NOTES.md`** | Markdown companion guide for presentation preparation |
| **`ARCHITECTURE_AND_COMPONENTS.md`** | Comprehensive architectural deep-dive and component reference manual explaining every file, class, method, and variable |

---

## Codebase Structure

| File | Component Description |
|---|---|
| `models.py` | `Transaction`, `Block`, `MerkleTree` — Data structures + SECP256k1 ECDSA signing + canonical SHA-256 serialization |
| `validator.py` | `MedicalAllocationValidator` — ABO blood compatibility, cold-ischemic countdown, and deterministic priority scoring gatekeeper |
| `blockchain.py` | `TransplantBlockchain` — Mempool, PoW mining, sibling double-claim resolution, and Nakamoto chain replay consensus |
| `synthetic_data.py` | Realistic clinical dataset generator providing synthetic patients, organs, HLA profiles, and MELD scores |
| `node.py` | RESTful Flask HTTP daemon turning the blockchain into an independent distributed P2P node |
| `run_network_demo.py` | Automated 3-node P2P mesh network demonstration (gossip, propagation, partition, concurrent fork mining, and reorganization) |
| `benchmark.py` | Quantitative benchmarking suite measuring matching latency vs. waitlist size and PoW mining scaling |
| `demo_correctness_fixes.py` | Adversarial edge-case security suite testing queue-jumping, expired organs, sibling mempool collisions, and ABO mismatches |
| `app.py` | Interactive Streamlit web dashboard with live organ inventory, transparent waitlist ranking, attack simulations, and block explorer |
| `diagrams/` | Pre-generated high-resolution architecture diagrams (`architecture_pipeline.png`, `architecture_network_fork.png`) |
| `results/` | Pre-generated benchmark plots and empirical CSV datasets (`matching_time_vs_waitlist.png`, `mining_time_vs_difficulty.png`) |
| `requirements.txt` | Minimal Python package dependencies |

---

## Quickstart & Execution Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Interactive Web Dashboard
```bash
streamlit run app.py
```
* **Fair Allocation:** Select an available organ $\rightarrow$ click *Submit Legitimate Allocation to Mempool* $\rightarrow$ click *Mine Pending Transactions*.
* **Live Attack Demonstration:** Navigate to the *Attack Demonstration* tab $\rightarrow$ click *Execute Queue-Jumping Attack* or *Execute Expired Organ Attack* to witness consensus rejection in real time.

### 3. Run Automated 3-Node Distributed Network Demo
```bash
python run_network_demo.py
```
Launches 3 independent processes (Donor Hospital, Recipient Hospital, Regulatory OPO), simulates full mesh gossip, block propagation, a network partition, concurrent fork mining, and automated Nakamoto reorganization.

### 4. Run Adversarial Security Tests
```bash
python demo_correctness_fixes.py
```
Validates that the protocol catches and rejects all 4 major attack vectors.

### 5. Run Empirical Benchmarks
```bash
python benchmark.py
```
Measures candidate matching latency and PoW mining curves, updating the CSVs and plots in `results/`.
