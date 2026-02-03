"""
=========================================================
Dufresne Quantum Purification Protocol
=========================================================
Author: Martin Dufresne
Affiliation: Cégep de St-Félicien
Date: February 2026
License: MIT
Paper: "Experimental Demonstration of Variational Entanglement Purification..."

Description:
This module implements a Variational Quantum Circuit (VQC) designed 
to purify noisy Bell pairs on superconducting hardware.
Optimized specifically for the IBM Eagle architecture (ibm_fez).

Usage:
    >>> from dufresne_quantum import DufresneProtocol
    >>> protocol = DufresneProtocol()
    >>> protocol.apply(wires_alice=[0, 2], wires_bob=[1, 3])
"""

import pennylane as qml
from pennylane import numpy as np

class DufresneProtocol:
    """
    Implémentation de l'opérateur de Dufresne pour la purification de qubits.
    """
    
    def __init__(self):
        # Les 18 coefficients de Dufresne (Optimisés via VQC)
        self.params = np.array([
            0.1852, 4.8917, 2.4693,  # Alice Input
            4.3103, 3.1853, 5.0678,  # Alice Sacrifice
            -0.2313, 4.9716, 3.7981, # Bob Input
            -0.0077, 0.0623, 3.9007, # Bob Sacrifice
            3.9007, 5.1955, -0.1021, # Mesure Alice (Smart Filter)
            5.3151, 2.0033, 2.9515   # Mesure Bob (Smart Filter)
        ])
    
    def apply(self, wires_alice=[0, 2], wires_bob=[1, 3]):
        """
        Applique l'opérateur U_Dufresne au circuit en cours.
        wires_alice : Liste des indices [Signal, Sacrifice] pour Alice
        wires_bob   : Liste des indices [Signal, Sacrifice] pour Bob
        """
        p = self.params
        
        # 1. Rotations d'Entrée (Input Rotation)
        qml.Rot(p[0], p[1], p[2], wires=wires_alice[0]) 
        qml.Rot(p[3], p[4], p[5], wires=wires_alice[1])
        qml.Rot(p[6], p[7], p[8], wires=wires_bob[0])
        qml.Rot(p[9], p[10], p[11], wires=wires_bob[1])

        # 2. Distillation (CNOT Bilatéral)
        qml.CNOT(wires=[wires_alice[0], wires_alice[1]])
        qml.CNOT(wires=[wires_bob[0], wires_bob[1]])

        # 3. Filtre de Mesure (Smart Measurement)
        qml.Rot(p[12], p[13], p[14], wires=wires_alice[1])
        qml.Rot(p[15], p[16], p[17], wires=wires_bob[1])

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    print("Initialisation du Protocole Dufresne...")
    protocol = DufresneProtocol()
    print(f"Coefficients chargés : {protocol.params.shape[0]} paramètres.")
    print("L'opérateur est prêt à être intégré dans un circuit E91.")