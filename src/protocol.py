"""
Dufresne Protocol Implementation
================================
Contains the main class for the variational entanglement purification ansatz.
"""

import pennylane as qml
from pennylane import numpy as np

class DufresneProtocol:
    """
    Implements the Dufresne Entanglement Purification Protocol.
    
    This class encapsulates the 18-parameter ansatz optimized for the IBM Eagle 
    architecture (ibm_fez). It applies asymmetric local rotations to filter 
    hardware-specific noise before and after the standard CNOT distillation.
    
    Attributes:
        params (np.array): The 18 optimized rotation angles (radians).
    """
    
    def __init__(self):
        # These parameters were obtained via VQC optimization on a 
        # noisy simulator (Depolarizing Noise ~5%)
        self.params = np.array([
            0.1852, 4.8917, 2.4693,  # Alice Input Rotations (Qubit 0)
            4.3103, 3.1853, 5.0678,  # Alice Sacrifice Rotations (Qubit 2)
            -0.2313, 4.9716, 3.7981, # Bob Input Rotations (Qubit 1)
            -0.0077, 0.0623, 3.9007, # Bob Sacrifice Rotations (Qubit 3)
            3.9007, 5.1955, -0.1021, # Alice Smart Measurement (Qubit 2)
            5.3151, 2.0033, 2.9515   # Bob Smart Measurement (Qubit 3)
        ])

    def apply(self, wires_alice=[0, 2], wires_bob=[1, 3]):
        """
        Applies the protocol operations to the active PennyLane circuit.
        
        Args:
            wires_alice (list): Indices of Alice's qubits [Signal, Sacrifice].
            wires_bob (list): Indices of Bob's qubits [Signal, Sacrifice].
        """
        p = self.params
        a_sig, a_sac = wires_alice
        b_sig, b_sac = wires_bob
        
        # 1. Input Correction Layer (VQC)
        # Corrects initial state preparation errors
        qml.Rot(p[0], p[1], p[2], wires=a_sig) 
        qml.Rot(p[3], p[4], p[5], wires=a_sac)
        qml.Rot(p[6], p[7], p[8], wires=b_sig)
        qml.Rot(p[9], p[10], p[11], wires=b_sac)

        # 2. Distillation Core (Standard Logic)
        # The bilateral CNOT operation checks parity
        qml.CNOT(wires=[a_sig, a_sac])
        qml.CNOT(wires=[b_sig, b_sac])

        # 3. Output Measurement Layer (Smart Filter)
        # Rotates the measurement basis to capture residual correlations
        qml.Rot(p[12], p[13], p[14], wires=a_sac)
        qml.Rot(p[15], p[16], p[17], wires=b_sac)

    def get_info(self):
        """Returns metadata about the protocol."""
        return {
            "name": "Dufresne Protocol",
            "type": "Variational Quantum Circuit (VQC)",
            "parameters": 18,
            "target_hardware": "IBM Eagle (Superconducting)"
        }