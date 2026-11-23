"""
blockchain.py
Consensus engine, state machine, mempool management, and chain replay
for TransplantChain. Implements Nakamoto consensus and sibling-conflict resolution.
"""
import copy
from models import Block, Transaction
from validator import MedicalAllocationValidator

GENESIS_PUBKEY = "00" * 32


def clone_validator(validator):
    """Creates a deep copy of the validator state for isolated tentative validation."""
    clone = MedicalAllocationValidator(use_index=validator.use_index)
    clone.active_organs = copy.deepcopy(validator.active_organs)
    clone.active_patients = copy.deepcopy(validator.active_patients)
    clone.allocations = copy.deepcopy(validator.allocations)
    return clone


def apply_transaction(tx, validator):
    """The Single Source of Truth for state transitions.
    Used uniformly for:
    1. Mempool admission
    2. Block assembly
    3. Peer block reception
    4. Full chain replay from Genesis
    """
    # Verify cryptographic signature (Genesis excepted)
    if tx.sender_pubkey != GENESIS_PUBKEY and not tx.verify_signature():
        return False, "Cryptographic Error: Invalid ECDSA signature."

    p = tx.payload

    if tx.tx_type == "REGISTER_ORGAN":
        organ_id = p.get("organ_id")
        if not organ_id or organ_id in validator.active_organs:
            return False, f"Duplicate Organ ID: '{organ_id}' already registered."
        validator.register_organ(organ_id, p)
        return True, f"Organ '{organ_id}' registered successfully."

    elif tx.tx_type == "REGISTER_PATIENT":
        patient_id = p.get("patient_id")
        if not patient_id or patient_id in validator.active_patients:
            return False, f"Duplicate Patient ID: '{patient_id}' already registered."
        validator.register_patient(patient_id, p)
        return True, f"Patient '{patient_id}' registered successfully."

    elif tx.tx_type == "ALLOCATE_ORGAN":
        organ_id = p.get("organ_id")
        patient_id = p.get("patient_id")
        alloc_time = p.get("allocation_time", tx.timestamp)
        ok, reason = validator.validate_allocation(organ_id, patient_id, alloc_time)
        if not ok:
            return False, reason
        validator.apply_allocation(organ_id, patient_id)
        return True, f"Organ '{organ_id}' allocated to patient '{patient_id}'."

    return False, f"Unknown Transaction Type: '{tx.tx_type}'."


class TransplantBlockchain:
    """Manages the distributed ledger, mempool, PoW consensus, and chain reorganization."""

    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.chain = []
        self.mempool = []
        self.validator = MedicalAllocationValidator()
        self.create_genesis_block()

    def create_genesis_block(self):
        """Initializes Block #0 with a Genesis transaction."""
        genesis_tx = Transaction(
            tx_type="REGISTER_ORGAN",
            sender_pubkey=GENESIS_PUBKEY,
            payload={
                "organ_id": "GENESIS_ORGAN",
                "organ_type": "Kidney",
                "donor_blood_type": "O",
                "donor_hla": ["A1", "B8", "DR3"],
                "harvest_time": 0,
                "max_ischemia_hours": 999999,
                "hospital_id": "GENESIS_NODE",
            },
            timestamp=0,
        )
        genesis_block = Block(
            index=0,
            previous_hash="0" * 64,
            transactions=[genesis_tx],
            difficulty=self.difficulty,
            timestamp=0,
        )
        self.chain.append(genesis_block)
        apply_transaction(genesis_tx, self.validator)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        """Validates a transaction against a temporary state clone before mempool entry."""
        if any(tx.tx_id == transaction.tx_id for tx in self.mempool):
            return False, "Duplicate Transaction: already in mempool."

        temp_validator = clone_validator(self.validator)
        ok, reason = apply_transaction(transaction, temp_validator)
        if not ok:
            return False, reason

        self.mempool.append(transaction)
        return True, "Transaction validated and added to Mempool."

    def mine_mempool(self):
        """Assembles a block by sequentially re-validating mempool transactions.
        Resolves sibling race conditions (e.g. conflicting allocations for the same organ).
        """
        if not self.mempool:
            return None, "Mempool is empty."

        working_validator = clone_validator(self.validator)
        included = []
        dropped = []

        for tx in self.mempool:
            ok, reason = apply_transaction(tx, working_validator)
            if ok:
                included.append(tx)
            else:
                dropped.append((tx, reason))

        self.mempool = []

        if not included:
            return None, "All mempool transactions conflicted with each other; nothing mined."

        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=included,
            difficulty=self.difficulty,
        )
        self.chain.append(new_block)
        self.validator = working_validator

        msg = f"Block #{new_block.index} mined successfully ({len(included)} txs)."
        if dropped:
            drop_details = "; ".join(f"{tx.tx_id[:8]}: {r}" for tx, r in dropped)
            msg += f" Dropped {len(dropped)} conflicting txs: {drop_details}"
        return new_block, msg

    def verify_chain_integrity(self):
        """Validates internal block hashes and Proof-of-Work links."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False, f"Block {i} hash altered."
            if current.previous_hash != prev.hash:
                return False, f"Block {i} previous hash link broken."
            if not current.hash.startswith("0" * self.difficulty):
                return False, f"Block {i} violates PoW difficulty."
        return True, "Blockchain state is fully valid and untampered."

    def try_append_block(self, block):
        """Appends a peer-mined block after verifying hashes and replaying transactions."""
        if block.index != len(self.chain):
            return False, "Index mismatch."
        if block.previous_hash != self.get_latest_block().hash:
            return False, "Previous hash reference mismatch."
        if not block.is_valid():
            return False, "Block failed internal cryptographic checks."

        temp_validator = clone_validator(self.validator)
        for tx in block.transactions:
            ok, reason = apply_transaction(tx, temp_validator)
            if not ok:
                return False, f"Block contains invalid transaction: {reason}"

        self.chain.append(block)
        self.validator = temp_validator
        incoming_ids = {tx.tx_id for tx in block.transactions}
        self.mempool = [t for t in self.mempool if t.tx_id not in incoming_ids]
        return True, "Block appended."

    @staticmethod
    def is_valid_chain(blocks, difficulty):
        """Re-derives the full candidate chain from Genesis, replaying all medical rules."""
        if not blocks or blocks[0].index != 0 or blocks[0].previous_hash != "0" * 64:
            return False, None

        validator = MedicalAllocationValidator()
        for i, block in enumerate(blocks):
            if block.index != i or not block.is_valid():
                return False, None
            if i > 0 and block.previous_hash != blocks[i - 1].hash:
                return False, None
            if not block.hash.startswith("0" * difficulty):
                return False, None
            for tx in block.transactions:
                ok, _ = apply_transaction(tx, validator)
                if not ok:
                    return False, None

        return True, validator

    def replace_chain(self, candidate_blocks):
        """Nakamoto Consensus: Adopts candidate chain if strictly longer and fully valid."""
        if len(candidate_blocks) <= len(self.chain):
            return False, "Candidate chain is not longer."

        ok, validator = self.is_valid_chain(candidate_blocks, self.difficulty)
        if not ok:
            return False, "Candidate chain failed full replay validation."

        self.chain = candidate_blocks
        self.validator = validator
        confirmed_ids = {t.tx_id for b in candidate_blocks for t in b.transactions}
        self.mempool = [t for t in self.mempool if t.tx_id not in confirmed_ids]
        return True, f"Chain reorganized. New tip height: {len(self.chain) - 1}."
