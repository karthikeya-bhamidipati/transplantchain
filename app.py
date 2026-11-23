"""
app.py - TransplantChain Clinical Command Center & Consensus Dashboard
A high-tech, medical-grade decentralized organ allocation protocol dashboard.
Provides real-time cryo-telemetry, cold-ischemia monitoring, deterministic waitlist auditing,
adversarial attack simulations, Proof-of-Work mining, and an immutable Merkle ledger explorer.
"""
import time
import streamlit as st
from ecdsa import SigningKey, SECP256k1

from blockchain import TransplantBlockchain
from models import Transaction
from synthetic_data import seed_blockchain

# Page Configuration
st.set_page_config(
    layout="wide",
    page_title="TransplantChain // Medical Consensus Command Center",
    page_icon="🫀",
    initial_sidebar_state="collapsed",
)

# Initialize / Cache Blockchain State
@st.cache_resource
def init_blockchain():
    bc = TransplantBlockchain(difficulty=2)
    sk = SigningKey.generate(curve=SECP256k1)
    priv = sk.to_string().hex()
    pub = sk.verifying_key.to_string().hex()
    seed_blockchain(bc, priv, pub)
    return bc, priv, pub

blockchain, admin_priv, admin_pub = init_blockchain()

# Inject Modern Command-Center Glassmorphism & Cyber-Medical Styling
st.markdown(
    """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Dark Slate Theme Background */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #0d1322 50%, #0a0f1d 100%);
        color: #e2e8f0;
    }

    /* Top Command Center Header */
    .command-header {
        background: rgba(19, 27, 46, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 12px #10b981;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }

    .title-gradient {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    .subtitle-text {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 0;
    }

    /* Telemetry HUD Metric Cards */
    .hud-card {
        background: rgba(22, 32, 54, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 14px;
        padding: 18px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    .hud-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
    }

    .hud-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #64748b;
        margin-bottom: 6px;
    }

    .hud-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px;
        font-weight: 800;
        color: #f8fafc;
    }

    .hud-sub {
        font-size: 12px;
        color: #38bdf8;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Organ Card in Cryo-Rack */
    .organ-rack-card {
        background: rgba(20, 30, 50, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        transition: all 0.25s ease;
    }

    .organ-rack-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(25, 38, 64, 0.85);
    }

    /* Custom Progress Bar */
    .ischemia-meter-container {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 8px;
        height: 10px;
        width: 100%;
        overflow: hidden;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .ischemia-meter-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.4s ease;
    }

    /* Candidate Match Card */
    .candidate-match-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 14px;
        padding: 22px;
        margin-top: 15px;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.12);
    }

    /* Attack Alert Box */
    .attack-alert-box {
        background: linear-gradient(135deg, rgba(76, 5, 25, 0.45) 0%, rgba(30, 10, 18, 0.6) 100%);
        border: 1px solid rgba(244, 63, 94, 0.6);
        border-radius: 14px;
        padding: 20px;
        color: #fecdd3;
        margin-top: 18px;
        box-shadow: 0 0 25px rgba(244, 63, 94, 0.2);
    }

    /* Streamlit Tab Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.15);
        margin-bottom: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 189, 248, 0.2) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }

    /* Primary Buttons */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# TOP HEADER: CLINICAL PROTOCOL COMMAND CENTER
# =============================================================================
st.markdown(
    """
    <div class="command-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div class="status-badge">
                <span class="pulse-dot"></span>
                <span>P2P NETWORK ONLINE • NAKAMOTO PoW CONSENSUS ACTIVE</span>
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748b;">
                NODE ID: <span style="color: #38bdf8;">HOSP-VALIDATOR-01</span> &nbsp;|&nbsp; 
                PROTOCOL: <span style="color: #38bdf8;">SECP256k1-SHA256-PoW</span>
            </div>
        </div>
        <div class="title-gradient">🫀 TransplantChain Command Center</div>
        <div class="subtitle-text">
            Decentralized Organ Allocation Protocol with Consensus-Enforced Medical Fairness & Cold-Ischemia Verification
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# TELEMETRY HUD RIBBON: 4 HIGH-TECH METRIC CARDS
# =============================================================================
h1, h2, h3, h4 = st.columns(4)

total_height = len(blockchain.chain) - 1
active_organs_count = sum(1 for o in blockchain.validator.active_organs.values() if o["status"] == "AVAILABLE")
waitlisted_count = sum(1 for p in blockchain.validator.active_patients.values() if p["status"] == "WAITLISTED")
confirmed_count = len(blockchain.validator.allocations)

with h1:
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-label">⛓️ Blockchain Height</div>
            <div class="hud-value" style="color: #38bdf8;">#{total_height}</div>
            <div class="hud-sub">Proof-of-Work Target: 0x00...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h2:
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-label">❄️ Cryo-Stored Organs</div>
            <div class="hud-value" style="color: #34d399;">{active_organs_count}</div>
            <div class="hud-sub">Viable & Awaiting Allocation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h3:
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-label">📋 Registered Candidates</div>
            <div class="hud-value" style="color: #fbbf24;">{waitlisted_count}</div>
            <div class="hud-sub">Auditable Deterministic MELD</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h4:
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-label">✅ Confirmed Transplants</div>
            <div class="hud-value" style="color: #a78bfa;">{confirmed_count}</div>
            <div class="hud-sub">Cryptographically Committed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")  # Vertical spacer

# =============================================================================
# MAIN NAVIGATION: 5 HIGH-TECH OPERATIONAL TABS
# =============================================================================
tab_clinical, tab_waitlist, tab_adversarial, tab_consensus, tab_registry = st.tabs([
    "🫀 Live Matching & Cryo-Racks",
    "📋 Transparent Patient Waitlist",
    "🛡️ Adversarial Security Console",
    "⛏️ PoW Miner & Block Explorer",
    "➕ Registry Intake Portal",
])

organs = blockchain.validator.active_organs
patients = blockchain.validator.active_patients

# =============================================================================
# TAB 1: LIVE ORGAN INVENTORY & SMART ALLOCATION
# =============================================================================
with tab_clinical:
    c_left, c_right = st.columns([1.1, 1.2], gap="large")

    with c_left:
        st.markdown("### ❄️ Cryo-Preserved Organ Telemetry")
        st.caption("Live physiological monitoring & Cold-Ischemia countdown clock for donor organs.")

        viable_organs = [o for oid, o in organs.items() if oid != "GENESIS_ORGAN"]

        if not viable_organs:
            st.info("No donor organs currently registered in protocol state.")
        else:
            for o in viable_organs:
                oid = o["organ_id"]
                elapsed_h = (time.time() - o["harvest_time"]) / 3600.0
                max_h = o["max_ischemia_hours"]
                pct_left = max(0.0, min(1.0, (max_h - elapsed_h) / max_h)) if max_h > 0 else 0

                is_viable = elapsed_h <= max_h
                status = o["status"]

                if status == "ALLOCATED":
                    status_text = "CONFIRMED ALLOCATED"
                    badge_bg = "rgba(167, 139, 250, 0.2)"
                    badge_color = "#c084fc"
                    meter_color = "linear-gradient(90deg, #818cf8, #a78bfa)"
                elif is_viable and status == "AVAILABLE":
                    status_text = "CLINICALLY VIABLE"
                    badge_bg = "rgba(16, 185, 129, 0.2)"
                    badge_color = "#34d399"
                    meter_color = "linear-gradient(90deg, #10b981, #38bdf8)"
                else:
                    status_text = "EXPIRED UNVIABLE"
                    badge_bg = "rgba(244, 63, 94, 0.2)"
                    badge_color = "#f43f5e"
                    meter_color = "linear-gradient(90deg, #f43f5e, #e11d48)"

                st.markdown(
                    f"""
                    <div class="organ-rack-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 17px; font-weight: 700; color: #f1f5f9;">
                                {o['organ_type']} <span style="font-family: 'JetBrains Mono'; font-size: 13px; color: #38bdf8;">({oid})</span>
                            </span>
                            <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}40; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;">
                                {status_text}
                            </span>
                        </div>
                        <div style="display: flex; gap: 16px; margin-top: 10px; font-size: 13px; color: #94a3b8;">
                            <span>🩸 Blood Group: <b style="color: #f8fafc;">{o['donor_blood_type']}</b></span>
                            <span>🏥 Hospital: <b style="color: #f8fafc;">{o['hospital_id']}</b></span>
                            <span>🧬 HLA: <b style="color: #38bdf8; font-family: 'JetBrains Mono';">{', '.join(o['donor_hla'])}</b></span>
                        </div>
                        <div style="margin-top: 12px;">
                            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; font-weight: 500;">
                                <span>Cold Ischemia Window: {elapsed_h:.1f}h / {max_h:.0f}h max</span>
                                <span style="font-family: 'JetBrains Mono'; color: {badge_color};">{pct_left*100:.0f}% Viability</span>
                            </div>
                            <div class="ischemia-meter-container">
                                <div class="ischemia-meter-fill" style="width: {pct_left*100}%; background: {meter_color};"></div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with c_right:
        st.markdown("### ⚖️ Protocol Allocation & Medical Matching")
        st.caption("Matches donor organs to the mathematically highest-priority eligible recipient.")

        available_list = [
            oid for oid, o in organs.items()
            if o["status"] == "AVAILABLE" and oid != "GENESIS_ORGAN"
            and (time.time() - o["harvest_time"]) / 3600.0 <= o["max_ischemia_hours"]
        ]

        if not available_list:
            st.warning("⚠️ No clinically viable organs currently available for allocation.")
        else:
            selected_organ_id = st.selectbox(
                "Select Available Donor Organ for Allocation",
                available_list,
                format_func=lambda x: f"{organs[x]['organ_type']} — {x} (Blood: {organs[x]['donor_blood_type']})",
            )
            organ_obj = organs[selected_organ_id]

            # Compute eligible candidates via validator
            eligible = blockchain.validator.get_eligible_candidates(organ_obj)

            if not eligible:
                st.error("❌ No eligible ABO-compatible candidates found on the waitlist for this organ.")
            else:
                top = eligible[0]
                st.markdown(
                    f"""
                    <div class="candidate-match-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <span style="font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; color: #34d399;">
                                🎯 MATHEMATICALLY HIGHEST-PRIORITY RECIPIENT
                            </span>
                            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 8px; border-radius: 8px; font-family: 'JetBrains Mono'; font-size: 12px;">
                                RANK #1
                            </span>
                        </div>
                        <div style="font-size: 22px; font-weight: 800; color: #f8fafc; font-family: 'JetBrains Mono';">
                            {top['patient_id']}
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                            <div>
                                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">URGENCY (MELD)</div>
                                <div style="font-size: 18px; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono';">{top['urgency_score']}</div>
                            </div>
                            <div>
                                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">WAITING DAYS</div>
                                <div style="font-size: 18px; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono';">{top['waiting_days']}d</div>
                            </div>
                            <div>
                                <div style="font-size: 11px; color: #94a3b8; font-weight: 600;">HLA MATCHES</div>
                                <div style="font-size: 18px; font-weight: 800; color: #a78bfa; font-family: 'JetBrains Mono';">{top['hla_matches']} / 6</div>
                            </div>
                        </div>
                        <div style="margin-top: 16px; padding: 10px 14px; background: rgba(15, 23, 42, 0.6); border-radius: 8px; font-size: 13px;">
                            <span style="color: #94a3b8;">Deterministic Score Formula:</span>
                            <b style="color: #34d399; font-family: 'JetBrains Mono'; margin-left: 8px;">{top['score']} pts</b>
                            <div style="font-size: 11px; color: #64748b; margin-top: 3px;">
                                {top['urgency_score']} + (0.01 × {top['waiting_days']}) + (1.5 × {top['hla_matches']}) = {top['score']}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.write("")
                if st.button("⚡ Authorize & Sign Allocation to Mempool", type="primary", use_container_width=True):
                    tx = Transaction("ALLOCATE_ORGAN", admin_pub, {
                        "organ_id": selected_organ_id,
                        "patient_id": top["patient_id"],
                        "allocation_time": time.time(),
                    })
                    tx.sign_transaction(admin_priv)
                    success, msg = blockchain.add_transaction(tx)
                    if success:
                        st.success(f"✅ Allocation Admitted to Mempool! {msg}")
                    else:
                        st.error(f"❌ Protocol Rejection: {msg}")

# =============================================================================
# TAB 2: TRANSPARENT PATIENT WAITLIST
# =============================================================================
with tab_waitlist:
    st.markdown("### 📋 Transparent Patient Waitlist (Algorithmic Ranking)")
    st.caption("Immutable waitlist where candidate priority is deterministically computed by Layer-1 consensus.")

    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px;">
            <span style="color: #38bdf8; font-weight: 700;">📐 Open Mathematical Ranking Formula:</span>
            <code style="background: rgba(15, 23, 42, 0.8); color: #34d399; padding: 3px 8px; border-radius: 6px; margin-left: 8px;">
                Priority Score = Urgency (MELD 6-40) + (0.01 × Waiting Days) + (1.5 × HLA Antigen Matches)
            </code>
            <p style="margin: 6px 0 0 0; font-size: 12px; color: #94a3b8;">
                Eliminates subjective administrative overrides, DBA tampering, and VIP queue-skipping.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not patients:
        st.info("No patients currently on the waitlist.")
    else:
        filter_col, search_col = st.columns([1, 2])
        with filter_col:
            organ_filter = st.selectbox("Filter by Organ", ["All Organs", "Kidney", "Liver", "Heart", "Lung"])

        table_rows = []
        for pid, p in patients.items():
            if organ_filter != "All Organs" and p["organ_needed"] != organ_filter:
                continue

            status_style = "color: #34d399; font-weight: bold;" if p["status"] == "WAITLISTED" else "color: #a78bfa; font-weight: bold;"

            table_rows.append({
                "Patient ID": pid,
                "Organ Required": p["organ_needed"],
                "Blood Type": p["patient_blood_type"],
                "Urgency (MELD)": f"{p['urgency_score']:.1f}",
                "Waiting (Days)": f"{p['waiting_time_days']} d",
                "HLA Antigens": ", ".join(p.get("patient_hla", [])),
                "Hospital Node": p.get("hospital_id", "HOSP_DEFAULT"),
                "Status": p["status"],
            })

        st.dataframe(table_rows, use_container_width=True)

# =============================================================================
# TAB 3: ADVERSARIAL SECURITY CONSOLE
# =============================================================================
with tab_adversarial:
    st.markdown("### 🛡️ Adversarial Security & Consensus Attack Simulator")
    st.caption("Execute malicious clinical transactions to witness real-time Layer-1 consensus rejection.")

    attack_col, info_col = st.columns([1.1, 1], gap="large")

    with attack_col:
        attack_type = st.radio(
            "Select Attack Scenario to Simulate:",
            [
                "VIP Queue-Jumping (Bypassing Sicker Candidates)",
                "Clinically Expired Organ Allocation",
                "Immunological ABO Blood Mismatch",
            ],
            index=0,
        )

        st.write("")

        if attack_type == "VIP Queue-Jumping (Bypassing Sicker Candidates)":
            st.markdown(
                """
                <div style="background: rgba(76, 5, 25, 0.25); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <b style="color: #f43f5e;">Scenario Description:</b>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #fecdd3;">
                        A corrupt hospital administrator attempts to allocate a donor organ to a wealthy VIP candidate with low clinical urgency, bypassing a critically ill candidate at the top of the queue.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚨 Execute Queue-Jumping Attack", type="secondary", use_container_width=True):
                target_organ = None
                target_candidates = None
                for oid, o in organs.items():
                    if o["status"] == "AVAILABLE" and oid != "GENESIS_ORGAN":
                        cands = blockchain.validator.get_eligible_candidates(o)
                        if len(cands) >= 2:
                            target_organ = oid
                            target_candidates = cands
                            break

                if not target_organ:
                    st.warning("Ensure at least one available organ has multiple waitlisted candidates.")
                else:
                    vip = target_candidates[-1]  # Lowest priority eligible candidate
                    tx_attack = Transaction("ALLOCATE_ORGAN", admin_pub, {
                        "organ_id": target_organ,
                        "patient_id": vip["patient_id"],
                        "allocation_time": time.time(),
                    })
                    tx_attack.sign_transaction(admin_priv)
                    success, msg = blockchain.add_transaction(tx_attack)
                    st.markdown(
                        f"""
                        <div class="attack-alert-box">
                            <div style="display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 800; color: #f43f5e;">
                                <span>🛑</span> <span>ATTACK REJECTED BY CONSENSUS ENGINE!</span>
                            </div>
                            <div style="margin-top: 10px; font-family: 'JetBrains Mono'; font-size: 13px; color: #fecdd3; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                                {msg}
                            </div>
                            <div style="margin-top: 10px; font-size: 12px; color: #fb7185;">
                                <b>Consensus Invariant Enforced:</b> Algorithmic Fairness rule halted transaction from entering the mempool.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        elif attack_type == "Clinically Expired Organ Allocation":
            st.markdown(
                """
                <div style="background: rgba(76, 5, 25, 0.25); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <b style="color: #f43f5e;">Scenario Description:</b>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #fecdd3;">
                        Simulates attempting to allocate an organ harvested 30 hours ago, exceeding the biological cold-ischemic viability window (24h max for kidneys).
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚨 Execute Expired Organ Attack", type="secondary", use_container_width=True):
                tx_exp = Transaction("ALLOCATE_ORGAN", admin_pub, {
                    "organ_id": "DONOR-KIDNEY-EXPIRED",
                    "patient_id": "PATIENT-KIDNEY-001",
                    "allocation_time": time.time(),
                })
                tx_exp.sign_transaction(admin_priv)
                success, msg = blockchain.add_transaction(tx_exp)
                st.markdown(
                    f"""
                    <div class="attack-alert-box">
                        <div style="display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 800; color: #f43f5e;">
                            <span>🛑</span> <span>ATTACK REJECTED BY CONSENSUS ENGINE!</span>
                        </div>
                        <div style="margin-top: 10px; font-family: 'JetBrains Mono'; font-size: 13px; color: #fecdd3; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                            {msg}
                        </div>
                        <div style="margin-top: 10px; font-size: 12px; color: #fb7185;">
                            <b>Consensus Invariant Enforced:</b> Cold-Ischemia Viability Limit prevented transplantation of spoiled tissue.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        elif attack_type == "Immunological ABO Blood Mismatch":
            st.markdown(
                """
                <div style="background: rgba(76, 5, 25, 0.25); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <b style="color: #f43f5e;">Scenario Description:</b>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #fecdd3;">
                        Attempts to allocate a Blood Type B donor organ to a Blood Type A recipient, an immunological incompatibility that triggers acute hyperacute graft rejection.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("🚨 Execute Incompatible Blood Attack", type="secondary", use_container_width=True):
                tx_incomp = Transaction("ALLOCATE_ORGAN", admin_pub, {
                    "organ_id": "DONOR-LIVER-BETA",
                    "patient_id": "PATIENT-KIDNEY-003",
                    "allocation_time": time.time(),
                })
                tx_incomp.sign_transaction(admin_priv)
                success, msg = blockchain.add_transaction(tx_incomp)
                st.markdown(
                    f"""
                    <div class="attack-alert-box">
                        <div style="display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 800; color: #f43f5e;">
                            <span>🛑</span> <span>ATTACK REJECTED BY CONSENSUS ENGINE!</span>
                        </div>
                        <div style="margin-top: 10px; font-family: 'JetBrains Mono'; font-size: 13px; color: #fecdd3; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;">
                            {msg}
                        </div>
                        <div style="margin-top: 10px; font-size: 12px; color: #fb7185;">
                            <b>Consensus Invariant Enforced:</b> Immunological ABO Matrix halted cross-blood allocation.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with info_col:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 14px; padding: 22px;">
                <h4 style="color: #38bdf8; margin-top: 0;">🛡️ Protocol Defense Mechanics</h4>
                <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                    Unlike traditional EVM smart contracts where invalid logic still gets mined if gas is paid, 
                    <b>TransplantChain integrates medical rules into Layer-1 consensus</b>.
                </p>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 12px;">
                    <div style="margin-bottom: 8px;"><b>1. Node Perimeter Defense:</b> Transactions failing clinical rules are blocked with instant HTTP 400 errors.</div>
                    <div style="margin-bottom: 8px;"><b>2. Sibling Conflict Resolution:</b> In-order batch recheck in <code>mine_mempool()</code> eliminates competing double-claims.</div>
                    <div style="margin-bottom: 8px;"><b>3. Chain Replay Consensus:</b> If a rogue miner mints a fraudulent block, honest peer nodes re-derive states from Genesis #0 and reject the entire chain tip.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================================================================
# TAB 4: CONSENSUS ENGINE, MEMPOOL & BLOCK EXPLORER
# =============================================================================
with tab_consensus:
    col_mine, col_mempool = st.columns([1, 1], gap="large")

    with col_mine:
        st.markdown("### ⛏️ Proof-of-Work Mining Engine")
        st.markdown(
            f"""
            <div style="background: rgba(26, 38, 64, 0.6); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #fbbf24;">MINING DIFFICULTY</span>
                    <span style="font-family: 'JetBrains Mono'; color: #f8fafc; font-weight: 800;">Target: 0x{'0'*blockchain.difficulty}...</span>
                </div>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 8px;">
                    Computes canonical SHA-256 header hash over transactions structured in a balanced binary Merkle tree.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.button("🔨 Mine Pending Mempool Transactions", type="primary", use_container_width=True):
            block, msg = blockchain.mine_mempool()
            if block:
                st.success(f"🎉 {msg} | Block Hash: `{block.hash[:20]}...` | Nonce: `{block.nonce}`")
                st.rerun()
            else:
                st.warning(f"⚠️ {msg}")

    with col_mempool:
        st.markdown("### 📦 Mempool Transaction Queue")
        st.caption(f"Unmined transactions awaiting cryptographic confirmation: **{len(blockchain.mempool)}**")

        if not blockchain.mempool:
            st.info("Mempool is clean. All transactions are committed to the chain.")
        else:
            for tx in blockchain.mempool:
                st.markdown(
                    f"""
                    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; font-size: 13px;">
                            <b style="color: #38bdf8;">{tx.tx_type}</b>
                            <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #64748b;">ID: {tx.tx_id[:16]}...</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("")
    st.markdown("### 🔗 Immutable Blockchain & Merkle Root Explorer")

    for b in reversed(blockchain.chain):
        is_genesis = b.index == 0
        tag = "GENESIS BLOCK" if is_genesis else f"BLOCK #{b.index}"
        border_col = "rgba(16, 185, 129, 0.3)" if is_genesis else "rgba(56, 189, 248, 0.25)"

        with st.expander(f"📦 {tag} | Hash: {b.hash[:24]}... | Merkle Root: {b.merkle_root[:16]}... | Nonce: {b.nonce}"):
            b1, b2 = st.columns(2)
            with b1:
                st.markdown(f"**Block Index:** `#{b.index}`")
                st.markdown(f"**Block Hash:** `{b.hash}`")
                st.markdown(f"**Previous Hash:** `{b.previous_hash}`")
            with b2:
                st.markdown(f"**Merkle Root:** `{b.merkle_root}`")
                st.markdown(f"**Nonce:** `{b.nonce}` &nbsp;|&nbsp; **Difficulty:** `{b.difficulty}`")
                st.markdown(f"**Transactions:** `{len(b.transactions)}`")

            st.json({
                "index": b.index,
                "timestamp": b.timestamp,
                "merkle_root": b.merkle_root,
                "transactions": [
                    {
                        "tx_id": t.tx_id,
                        "tx_type": t.tx_type,
                        "sender": t.sender_pubkey[:16] + "...",
                        "payload": t.payload,
                    }
                    for t in b.transactions
                ],
            })

# =============================================================================
# TAB 5: REGISTRY INTAKE PORTAL
# =============================================================================
with tab_registry:
    st.markdown("### ➕ Clinical Intake: Register Patients & Donor Organs")
    st.caption("Cryptographically signs registration payloads with certified hospital private keys (SECP256k1).")

    r_col1, r_col2 = st.columns(2, gap="large")

    with r_col1:
        st.markdown("#### 👤 Register Waitlisted Candidate")
        c_pid = st.text_input("Patient ID", "PATIENT-REG-01")
        c_organ = st.selectbox("Organ Needed", ["Kidney", "Liver", "Heart", "Lung"])
        c_blood = st.selectbox("Blood Group", ["O", "A", "B", "AB"])
        c_urgency = st.slider("Urgency (MELD) Score", 6.0, 40.0, 32.5)
        c_wait = st.number_input("Waiting Days Accrued", value=180, min_value=0)
        c_hla = st.text_input("HLA Antigens (comma-separated)", "A2, B7, DR4")

        if st.button("Submit Patient Registration to Mempool", type="primary", use_container_width=True):
            hla_list = [h.strip() for h in c_hla.split(",") if h.strip()]
            tx_p = Transaction("REGISTER_PATIENT", admin_pub, {
                "patient_id": c_pid,
                "organ_needed": c_organ,
                "patient_blood_type": c_blood,
                "urgency_score": c_urgency,
                "waiting_time_days": c_wait,
                "patient_hla": hla_list,
                "hospital_id": "HOSP_METRO_01",
            })
            tx_p.sign_transaction(admin_priv)
            s, m = blockchain.add_transaction(tx_p)
            if s:
                st.success(f"✅ {m}")
            else:
                st.error(f"❌ {m}")

    with r_col2:
        st.markdown("#### 🫀 Register Harvested Donor Organ")
        c_oid = st.text_input("Donor Organ ID", "DONOR-REG-01")
        c_organ_type = st.selectbox("Organ Type", ["Kidney", "Liver", "Heart", "Lung"])
        c_donor_blood = st.selectbox("Donor Blood Group", ["O", "A", "B", "AB"])
        c_ischemia = st.number_input("Max Cold-Ischemia Limit (Hours)", value=24.0, min_value=1.0)
        c_donor_hla = st.text_input("Donor HLA Antigens (comma-separated)", "A2, B8, DR4")

        if st.button("Submit Donor Organ Registration to Mempool", type="primary", use_container_width=True):
            donor_hla_list = [h.strip() for h in c_donor_hla.split(",") if h.strip()]
            tx_o = Transaction("REGISTER_ORGAN", admin_pub, {
                "organ_id": c_oid,
                "organ_type": c_organ_type,
                "donor_blood_type": c_donor_blood,
                "harvest_time": time.time(),
                "max_ischemia_hours": c_ischemia,
                "donor_hla": donor_hla_list,
                "hospital_id": "OPO_METRO_01",
            })
            tx_o.sign_transaction(admin_priv)
            s, m = blockchain.add_transaction(tx_o)
            if s:
                st.success(f"✅ {m}")
            else:
                st.error(f"❌ {m}")
