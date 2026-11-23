"""
validator.py
Medical Allocation Gatekeeper for TransplantChain.
Enforces blood-type compatibility, HLA matching, cold-ischemic time limits,
and deterministic medical fairness (anti-queue-jumping) at the protocol level.
"""
import heapq
import time

# Standard clinical ABO blood compatibility matrix
# Key: Donor Blood Group -> Allowed Recipient Blood Groups
BLOOD_COMPATIBILITY = {
    "O":  {"O", "A", "B", "AB"},  # Universal donor
    "A":  {"A", "AB"},
    "B":  {"B", "AB"},
    "AB": {"AB"},                  # Universal recipient
}

# Standard clinical maximum cold-ischemia limits (in hours)
DEFAULT_ISCHEMIA_LIMITS = {
    "Heart": 4.0,
    "Lung": 6.0,
    "Liver": 12.0,
    "Pancreas": 12.0,
    "Kidney": 24.0,
}


def calculate_hla_matches(donor_hla, patient_hla):
    """Calculates number of shared HLA antigen matches (0 to 6)."""
    return len(set(donor_hla).intersection(set(patient_hla)))


def compute_priority_score(urgency_score, waiting_time_days, hla_matches):
    """Computes deterministic medical priority score:
    Score = Urgency (MELD 6-40) + (0.01 * Waiting Days) + (1.5 * HLA Matches)
    """
    return round(float(urgency_score) + (0.01 * float(waiting_time_days)) + (1.5 * float(hla_matches)), 4)


class MedicalAllocationValidator:
    """The Medical Gatekeeper enforcing clinical and fairness invariants.
    use_index=False forces a linear O(N) scan instead of indexed candidate sorting,
    allowing benchmark.py to measure empirical performance gains.
    """

    def __init__(self, use_index=True):
        self.use_index = use_index
        # State stores
        self.active_organs = {}     # organ_id -> dict of organ details
        self.active_patients = {}   # patient_id -> dict of patient details
        self.allocations = {}       # organ_id -> patient_id

    def register_organ(self, organ_id, payload):
        """Registers a newly harvested donor organ into state."""
        self.active_organs[organ_id] = {
            "organ_id": organ_id,
            "organ_type": payload["organ_type"],
            "donor_blood_type": payload["donor_blood_type"],
            "donor_hla": payload.get("donor_hla", []),
            "harvest_time": payload.get("harvest_time", time.time()),
            "max_ischemia_hours": payload.get("max_ischemia_hours",
                                              DEFAULT_ISCHEMIA_LIMITS.get(payload["organ_type"], 12.0)),
            "hospital_id": payload.get("hospital_id", "HOSP_DEFAULT"),
            "status": "AVAILABLE",
        }

    def register_patient(self, patient_id, payload):
        """Registers a waitlisted patient into state."""
        self.active_patients[patient_id] = {
            "patient_id": patient_id,
            "organ_needed": payload["organ_needed"],
            "patient_blood_type": payload["patient_blood_type"],
            "patient_hla": payload.get("patient_hla", []),
            "urgency_score": payload["urgency_score"],  # e.g. MELD score
            "waiting_time_days": payload.get("waiting_time_days", 0),
            "hospital_id": payload.get("hospital_id", "HOSP_DEFAULT"),
            "status": "WAITLISTED",
        }

    def get_eligible_candidates(self, organ):
        """Retrieves and scores all clinically eligible waitlist patients for an organ."""
        donor_blood = organ["donor_blood_type"]
        compatible_recipients = BLOOD_COMPATIBILITY.get(donor_blood, set())
        organ_type = organ["organ_type"]
        donor_hla = organ.get("donor_hla", [])

        candidates = []
        for pid, p in self.active_patients.items():
            if p["status"] != "WAITLISTED":
                continue
            if p["organ_needed"] != organ_type:
                continue
            if p["patient_blood_type"] not in compatible_recipients:
                continue

            hla_matches = calculate_hla_matches(donor_hla, p.get("patient_hla", []))
            score = compute_priority_score(p["urgency_score"], p["waiting_time_days"], hla_matches)
            candidates.append({
                "patient_id": pid,
                "score": score,
                "urgency_score": p["urgency_score"],
                "waiting_days": p["waiting_time_days"],
                "hla_matches": hla_matches,
                "blood_type": p["patient_blood_type"],
            })

        if self.use_index:
            # Sort candidates in descending order of priority score
            candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates

    def validate_allocation(self, organ_id, patient_id, allocation_time=None):
        """The Core Protocol Gatekeeper:
        Verifies existence, availability, cold-ischemic viability, and algorithmic fairness.
        """
        # Rule 1: Check organ validity
        if organ_id not in self.active_organs:
            return False, f"Organ Not Found: '{organ_id}' is not registered."
        organ = self.active_organs[organ_id]
        if organ["status"] != "AVAILABLE":
            return False, f"Double Allocation Error: Organ '{organ_id}' is already {organ['status']}."

        # Rule 2: Check patient validity
        if patient_id not in self.active_patients:
            return False, f"Patient Not Found: '{patient_id}' is not on the waitlist."
        patient = self.active_patients[patient_id]
        if patient["status"] != "WAITLISTED":
            return False, f"Patient State Error: Patient '{patient_id}' status is {patient['status']}."

        # Rule 3: Organ type match
        if organ["organ_type"] != patient["organ_needed"]:
            return False, f"Mismatched Organ Type: Organ is '{organ['organ_type']}' but patient needs '{patient['organ_needed']}'."

        # Rule 4: ABO Blood Compatibility
        allowed_recipients = BLOOD_COMPATIBILITY.get(organ["donor_blood_type"], set())
        if patient["patient_blood_type"] not in allowed_recipients:
            return False, (f"Immunological ABO Incompatibility: Donor blood type '{organ['donor_blood_type']}' "
                          f"is incompatible with recipient '{patient['patient_blood_type']}'.")

        # Rule 5: Cold Ischemia Viability Limit
        current_t = allocation_time if allocation_time is not None else time.time()
        elapsed_hours = (current_t - organ["harvest_time"]) / 3600.0
        if elapsed_hours > organ["max_ischemia_hours"]:
            return False, (f"Clinical Viability Error: Cold ischemic limit exceeded! "
                          f"Elapsed {elapsed_hours:.2f}h > Max allowed {organ['max_ischemia_hours']}h. "
                          f"Organ is clinically expired.")

        # Rule 6: Algorithmic Fairness / Anti-Queue-Jumping Invariant
        candidates = self.get_eligible_candidates(organ)
        if not candidates:
            return False, "Fairness Error: No eligible candidates found on waitlist."

        top_candidate = candidates[0]
        # Find proposed candidate's score
        proposed = next((c for c in candidates if c["patient_id"] == patient_id), None)
        if proposed is None:
            return False, f"Fairness Error: Proposed patient '{patient_id}' is not in the eligible candidate pool."

        # Reject if another patient has a strictly higher priority score (> 0.001 margin)
        if top_candidate["score"] - proposed["score"] > 0.001 and top_candidate["patient_id"] != patient_id:
            return False, (f"Fairness Violation (Queue-Jumping Detected): Proposed patient '{patient_id}' "
                          f"(Score: {proposed['score']}) bypassed higher-priority candidate "
                          f"'{top_candidate['patient_id']}' (Score: {top_candidate['score']}). "
                          f"Allocation rejected by protocol.")

        return True, "Valid Allocation"

    def apply_allocation(self, organ_id, patient_id):
        """Mutates authoritative state upon confirmed block commitment."""
        self.active_organs[organ_id]["status"] = "ALLOCATED"
        self.active_patients[patient_id]["status"] = "TRANSPLANTED"
        self.allocations[organ_id] = patient_id
