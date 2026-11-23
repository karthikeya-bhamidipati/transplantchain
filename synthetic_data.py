"""
synthetic_data.py
Realistic clinical synthetic data generator for TransplantChain.
Provides diverse patients, donor organs, blood groups, HLA antigen profiles,
and urgency (MELD) scores across multiple simulated hospital centers.
"""
import time
from ecdsa import SigningKey, SECP256k1
from models import Transaction

SAMPLE_HLA_POOLS = [
    ["A2", "A24", "B7", "B44", "DR4", "DR15"],
    ["A1", "A3", "B8", "B35", "DR3", "DR4"],
    ["A2", "A11", "B27", "B51", "DR1", "DR8"],
    ["A24", "A26", "B18", "B62", "DR11", "DR14"],
    ["A1", "A2", "B7", "B8", "DR3", "DR15"],
]

HOSPITALS = [
    "HOSP_METRO_GENERAL",
    "HOSP_ST_JUDE_MEDICAL",
    "HOSP_UNIVERSITY_HEALTH",
    "HOSP_APOLLO_TRANSPLANT",
]

# Realistic clinical patient profiles
SYNTHETIC_PATIENTS = [
    {
        "patient_id": "PATIENT-KIDNEY-001",
        "organ_needed": "Kidney",
        "patient_blood_type": "O",
        "patient_hla": ["A2", "A24", "B7", "B44", "DR4", "DR15"],
        "urgency_score": 38.5,  # High critical urgency
        "waiting_time_days": 420,
        "hospital_id": "HOSP_METRO_GENERAL",
    },
    {
        "patient_id": "PATIENT-KIDNEY-002",
        "organ_needed": "Kidney",
        "patient_blood_type": "O",
        "patient_hla": ["A2", "A24", "B8", "B35", "DR3", "DR4"],
        "urgency_score": 24.0,  # Moderate urgency
        "waiting_time_days": 180,
        "hospital_id": "HOSP_ST_JUDE_MEDICAL",
    },
    {
        "patient_id": "PATIENT-KIDNEY-003",
        "organ_needed": "Kidney",
        "patient_blood_type": "A",
        "patient_hla": ["A1", "A3", "B7", "B44", "DR1", "DR8"],
        "urgency_score": 31.0,
        "waiting_time_days": 310,
        "hospital_id": "HOSP_UNIVERSITY_HEALTH",
    },
    {
        "patient_id": "PATIENT-LIVER-101",
        "organ_needed": "Liver",
        "patient_blood_type": "B",
        "patient_hla": ["A24", "A26", "B18", "B62", "DR11", "DR14"],
        "urgency_score": 36.2,  # Severe acute liver failure (MELD 36)
        "waiting_time_days": 95,
        "hospital_id": "HOSP_APOLLO_TRANSPLANT",
    },
    {
        "patient_id": "PATIENT-LIVER-102",
        "organ_needed": "Liver",
        "patient_blood_type": "AB",
        "patient_hla": ["A1", "A2", "B7", "B8", "DR3", "DR15"],
        "urgency_score": 19.5,  # Stable MELD 19
        "waiting_time_days": 540,
        "hospital_id": "HOSP_METRO_GENERAL",
    },
    {
        "patient_id": "PATIENT-HEART-201",
        "organ_needed": "Heart",
        "patient_blood_type": "O",
        "patient_hla": ["A2", "A24", "B7", "B44", "DR4", "DR15"],
        "urgency_score": 39.8,  # Critical ICU Status 1A
        "waiting_time_days": 65,
        "hospital_id": "HOSP_ST_JUDE_MEDICAL",
    },
]

# Realistic donor organs (with varying harvest times and cold-ischemic windows)
def get_synthetic_organs(base_time=None):
    now = base_time if base_time is not None else time.time()
    return [
        {
            "organ_id": "DONOR-KIDNEY-ALPHA",
            "organ_type": "Kidney",
            "donor_blood_type": "O",
            "donor_hla": ["A2", "A24", "B7", "B44", "DR4", "DR15"],  # 6/6 perfect HLA match with KIDNEY-001
            "harvest_time": now - 3600 * 2,  # Harvested 2 hours ago (Viable for 24h)
            "max_ischemia_hours": 24.0,
            "hospital_id": "HOSP_METRO_GENERAL",
        },
        {
            "organ_id": "DONOR-LIVER-BETA",
            "organ_type": "Liver",
            "donor_blood_type": "B",
            "donor_hla": ["A24", "A26", "B18", "B62", "DR11", "DR14"],
            "harvest_time": now - 3600 * 4,  # Harvested 4 hours ago (Viable for 12h)
            "max_ischemia_hours": 12.0,
            "hospital_id": "HOSP_APOLLO_TRANSPLANT",
        },
        {
            "organ_id": "DONOR-HEART-GAMMA",
            "organ_type": "Heart",
            "donor_blood_type": "O",
            "donor_hla": ["A2", "A24", "B7", "B44", "DR4", "DR15"],
            "harvest_time": now - 3600 * 1.5,  # Harvested 1.5 hours ago (Viable for 4h)
            "max_ischemia_hours": 4.0,
            "hospital_id": "HOSP_ST_JUDE_MEDICAL",
        },
        {
            "organ_id": "DONOR-KIDNEY-EXPIRED",
            "organ_type": "Kidney",
            "donor_blood_type": "O",
            "donor_hla": ["A1", "A3", "B8", "B35", "DR3", "DR4"],
            "harvest_time": now - 3600 * 30,  # Harvested 30 hours ago! (Exceeded 24h limit)
            "max_ischemia_hours": 24.0,
            "hospital_id": "HOSP_UNIVERSITY_HEALTH",
        },
    ]


def generate_wallet():
    """Generates a private/public keypair using SECP256k1 curve."""
    sk = SigningKey.generate(curve=SECP256k1)
    priv_hex = sk.to_string().hex()
    pub_hex = sk.verifying_key.to_string().hex()
    return priv_hex, pub_hex


def seed_blockchain(blockchain, priv_hex, pub_hex):
    """Populates a blockchain instance with baseline synthetic patients and organs."""
    # Register patients
    for patient_data in SYNTHETIC_PATIENTS:
        tx = Transaction(
            tx_type="REGISTER_PATIENT",
            sender_pubkey=pub_hex,
            payload=patient_data,
        )
        tx.sign_transaction(priv_hex)
        blockchain.add_transaction(tx)

    # Register organs
    for organ_data in get_synthetic_organs():
        tx = Transaction(
            tx_type="REGISTER_ORGAN",
            sender_pubkey=pub_hex,
            payload=organ_data,
        )
        tx.sign_transaction(priv_hex)
        blockchain.add_transaction(tx)

    # Mine initial baseline block
    blockchain.mine_mempool()
