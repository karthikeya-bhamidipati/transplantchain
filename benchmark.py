"""
benchmark.py
Empirical performance benchmarking suite for TransplantChain:
1. Algorithmic candidate matching latency vs. waitlist size (Indexed vs. Brute-Force).
2. Proof-of-Work mining latency vs. difficulty target (1 to 6 hex zeros).
Generates CSV data and publication-quality plots in results/.
"""
import csv
import os
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models import Block, Transaction
from validator import MedicalAllocationValidator

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def generate_synthetic_patient(i):
    blood_types = ["O", "A", "B", "AB"]
    organs = ["Kidney", "Liver", "Heart"]
    return {
        "patient_id": f"P-{i}",
        "organ_needed": organs[i % len(organs)],
        "patient_blood_type": blood_types[i % len(blood_types)],
        "patient_hla": ["A2", "B7", "DR4"],
        "urgency_score": 15.0 + (i % 25),
        "waiting_time_days": i % 500,
        "hospital_id": f"HOSP_{i % 5}",
    }


def bench_matching_time_vs_waitlist(patient_counts, trials=20):
    rows = []
    print("\n--- Running Experiment 1: Matching Latency vs. Waitlist Size ---")
    for n in patient_counts:
        for use_index in (True, False):
            val = MedicalAllocationValidator(use_index=use_index)
            # Seed waitlist
            for i in range(n):
                val.register_patient(f"P-{i}", generate_synthetic_patient(i))

            organ = {
                "organ_id": "TEST_ORGAN",
                "organ_type": "Kidney",
                "donor_blood_type": "O",
                "donor_hla": ["A2", "B7", "DR4"],
                "harvest_time": time.time(),
                "max_ischemia_hours": 24.0,
            }

            start = time.perf_counter()
            for _ in range(trials):
                val.get_eligible_candidates(organ)
            elapsed = (time.perf_counter() - start) / trials

            rows.append({"n_patients": n, "indexed": use_index, "seconds_per_match": elapsed})
            mode = "Indexed" if use_index else "Brute-Force"
            print(f"  Waitlist: {n:>5} | Mode: {mode:12} | Avg Latency: {elapsed*1000:.4f} ms")
    return rows


def bench_mining_time_vs_difficulty(difficulties, trials=3):
    rows = []
    print("\n--- Running Experiment 2: Mining Latency vs. PoW Difficulty ---")
    for diff in difficulties:
        times = []
        for t in range(trials):
            tx = Transaction(
                tx_type="REGISTER_ORGAN",
                sender_pubkey="00" * 32,
                payload={"organ_id": f"BENCH-{diff}-{t}", "organ_type": "Kidney", "donor_blood_type": "O"},
            )
            start = time.perf_counter()
            Block(index=1, previous_hash="0" * 64, transactions=[tx], difficulty=diff)
            times.append(time.perf_counter() - start)
        avg = sum(times) / len(times)
        rows.append({"difficulty": diff, "avg_seconds": avg, "trials": trials})
        print(f"  Difficulty: {diff} (target '0'*{diff}) | Avg Mining Time: {avg:.4f} s")
    return rows


def plot_matching_time(rows):
    indexed_x = [r["n_patients"] for r in rows if r["indexed"]]
    indexed_y = [r["seconds_per_match"] * 1000 for r in rows if r["indexed"]]
    brute_x = [r["n_patients"] for r in rows if not r["indexed"]]
    brute_y = [r["seconds_per_match"] * 1000 for r in rows if not r["indexed"]]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    ax.plot(brute_x, brute_y, "o-", color="#dc2626", label="Linear Scan (Brute-Force O(N))", linewidth=2)
    ax.plot(indexed_x, indexed_y, "s-", color="#16a34a", label="Priority Indexed O(log N)", linewidth=2)

    ax.set_title("Organ Matching Latency vs. Waitlist Size", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Registered Waitlist Patients (N)", fontsize=10)
    ax.set_ylabel("Average Latency per Match (ms)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True)
    plt.tight_layout()

    out_path = os.path.join(RESULTS_DIR, "matching_time_vs_waitlist.png")
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved plot: {out_path}")


def plot_mining_time(rows):
    diffs = [r["difficulty"] for r in rows]
    times = [r["avg_seconds"] for r in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    ax.plot(diffs, times, "o-", color="#2563eb", linewidth=2, markersize=7)
    ax.set_yscale("log")
    ax.set_title("Proof-of-Work Mining Latency vs. Difficulty Target", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Difficulty (Required Leading Hex Zeros)", fontsize=10)
    ax.set_ylabel("Average Mining Time (seconds, log scale)", fontsize=10)
    ax.grid(True, which="both", linestyle="--", alpha=0.5)

    for d, t in zip(diffs, times):
        label = f"{t*1000:.1f}ms" if t < 1 else f"{t:.2f}s"
        ax.annotate(label, (d, t), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "mining_time_vs_difficulty.png")
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved plot: {out_path}")


def save_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved CSV: {path}")


def main():
    # 1. Matching Benchmark
    patient_counts = [10, 50, 100, 250, 500, 1000, 2500, 5000]
    match_rows = bench_matching_time_vs_waitlist(patient_counts)
    save_csv(os.path.join(RESULTS_DIR, "matching_time_vs_waitlist.csv"), match_rows,
             ["n_patients", "indexed", "seconds_per_match"])
    plot_matching_time(match_rows)

    # 2. Mining Benchmark
    difficulties = [1, 2, 3, 4, 5]
    mining_rows = bench_mining_time_vs_difficulty(difficulties)
    save_csv(os.path.join(RESULTS_DIR, "mining_time_vs_difficulty.csv"), mining_rows,
             ["difficulty", "avg_seconds", "trials"])
    plot_mining_time(mining_rows)


if __name__ == "__main__":
    main()
