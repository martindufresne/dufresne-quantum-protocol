"""
=========================================================
02_ibm_benchmark.py
=========================================================
Description:
Main script to execute the comparative benchmark on IBM Quantum hardware.
Compares the Standard Protocol (BBPSSW) vs. Dufresne Protocol (VQC).

Author: Martin Dufresne
Date: February 2026
"""

import pennylane as qml
from pennylane import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService
import os
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---

# Load environment variables from the .env file (security best practice)
load_dotenv()

TOKEN = os.getenv("IBM_QUANTUM_TOKEN")

try:
    if TOKEN:
        # Connect using the token from .env
        service = QiskitRuntimeService(channel="ibm_quantum", token=TOKEN)
    else:
        # Fallback: Try using the account saved locally on disk
        service = QiskitRuntimeService(channel="ibm_quantum")
        
    print("IBM Quantum Connection established.")

except Exception as e:
    print(f"Connection Error: {e}")
    print("Tip: Create a .env file with IBM_QUANTUM_TOKEN=your_token_here")
    exit()

# Select the least busy real backend (not a simulator) with at least 4 qubits
try:
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=4)
    print(f"Target Hardware: {backend.name} ({backend.num_qubits} qubits)")
except Exception as e:
    print("No operational backend found. Please check your IBM Quantum access.")
    exit()

# Initialize PennyLane device
# shots=1024 is the standard for statistical significance in this benchmark
dev = qml.device('qiskit.remote', wires=4, backend=backend, shots=1024)


# --- 2. PROTOCOL DEFINITIONS ---

# A. Optimized Parameters (Dufresne)
# These 18 angles were learned via VQC training to correct specific hardware noise.
PARAMS_DUFRESNE = np.array([
    0.1852, 4.8917, 2.4693, 
    4.3103, 3.1853, 5.0678, 
    -0.2313, 4.9716, 3.7981, 
    -0.0077, 0.0623, 3.9007, 
    3.9007, 5.1955, -0.1021, 
    5.3151, 2.0033, 2.9515   
])

# B. Standard Protocol (BBPSSW) - CONTROL GROUP
@qml.qnode(dev)
def standard_protocol():
    # 1. Noisy State Preparation (Simulating natural E91 distribution)
    qml.Hadamard(wires=0); qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=2); qml.CNOT(wires=[2, 3])

    # 2. Standard Distillation (Fixed CNOT gates)
    qml.CNOT(wires=[0, 2])
    qml.CNOT(wires=[1, 3])

    # 3. Standard Measurement (Z-Basis)
    return qml.counts(all_outcomes=True)

# C. Dufresne Protocol (VQC) - OUR METHOD
@qml.qnode(dev)
def dufresne_protocol(params):
    # 1. Noisy State Preparation
    qml.Hadamard(wires=0); qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=2); qml.CNOT(wires=[2, 3])

    # 2. VQC Correction (Rotations + CNOTs + Rotations)
    # Input Rotation Layer
    qml.Rot(params[0], params[1], params[2], wires=0) 
    qml.Rot(params[3], params[4], params[5], wires=2)
    qml.Rot(params[6], params[7], params[8], wires=1)
    qml.Rot(params[9], params[10], params[11], wires=3)

    # Distillation Core
    qml.CNOT(wires=[0, 2])
    qml.CNOT(wires=[1, 3])

    # Measurement Rotation Layer (Smart Filter)
    qml.Rot(params[12], params[13], params[14], wires=2)
    qml.Rot(params[15], params[16], params[17], wires=3)

    return qml.counts(all_outcomes=True)


# --- 3. BENCHMARK EXECUTION ---
if __name__ == "__main__":
    print("\nLaunching Comparative Benchmark...")
    print("(This may take several minutes depending on IBM queue status)")
    
    # Run 1 : Standard Protocol
    print("\n--- 1. Running Standard Protocol (BBPSSW) ---")
    res_std = standard_protocol()
    print(f"Raw Results (Standard): {res_std}")
    
    # Run 2 : Dufresne Protocol
    print("\n--- 2. Running Dufresne Protocol ---")
    res_duf = dufresne_protocol(PARAMS_DUFRESNE)
    print(f"Raw Results (Dufresne): {res_duf}")
    
    # Helper function to calculate fidelity
    def get_fidelity(counts):
        # Summing valid Bell states (00.. and 11..)
        # Note: In E91 purification, we check correlation on distilled pairs
        signal = counts.get('0000',0) + counts.get('0001',0) + counts.get('0010',0) + counts.get('0011',0) + \
                 counts.get('1100',0) + counts.get('1101',0) + counts.get('1110',0) + counts.get('1111',0)
        total = sum(counts.values())
        return signal / total if total > 0 else 0

    fid_std = get_fidelity(res_std)
    fid_duf = get_fidelity(res_duf)
    
    print("\n" + "="*40)
    print("FINAL BENCHMARK REPORT")
    print("="*40)
    print(f"Standard Fidelity : {fid_std:.2%}")
    print(f"Dufresne Fidelity : {fid_duf:.2%}")
    print(f"Improvement       : {fid_duf - fid_std:+.2%}")
    print("="*40)