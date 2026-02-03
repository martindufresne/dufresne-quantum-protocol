"""
01_optimization.py
==================
Training script for the Dufresne Protocol.
Uses a noisy simulator (Depolarizing Channel) and Adam Optimizer to find
the optimal rotation angles that maximize entanglement fidelity.
"""

import pennylane as qml
from pennylane import numpy as np

# --- CONFIGURATION ---
NOISE_LEVEL = 0.05  # 5% Noise (Simulating IBM Fez environment)
STEPS = 100         # Optimization steps
LEARNING_RATE = 0.1

# Setup a noisy simulator
dev = qml.device('default.mixed', wires=4)

def noise_layer():
    """Injects symmetric noise to simulate optical fibers or hardware errors."""
    for i in range(4):
        qml.DepolarizingChannel(NOISE_LEVEL, wires=i)

@qml.qnode(dev)
def cost_circuit(params):
    # 1. State Preparation (Bell Pairs)
    qml.Hadamard(wires=0); qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=2); qml.CNOT(wires=[2, 3])
    
    # Inject Noise
    noise_layer()

    # 2. Ansatz Application (The Learning Part)
    # Alice's side
    qml.Rot(params[0], params[1], params[2], wires=0)
    qml.Rot(params[3], params[4], params[5], wires=2)
    # Bob's side
    qml.Rot(params[6], params[7], params[8], wires=1)
    qml.Rot(params[9], params[10], params[11], wires=3)

    # Distillation Logic
    qml.CNOT(wires=[0, 2])
    qml.CNOT(wires=[1, 3])

    # Measurement Layer
    qml.Rot(params[12], params[13], params[14], wires=2)
    qml.Rot(params[15], params[16], params[17], wires=3)

    # We want to maximize the probability of getting |00> on the signal pair
    # provided that the sacrifice pair measured |00> (success case)
    return qml.density_matrix(wires=[0, 1])

def cost_fn(params):
    """
    Cost function: 1 - Fidelity of the output state compared to ideal Bell state.
    """
    rho_out = cost_circuit(params)
    
    # Ideal Bell State |Phi+>
    bell_state = np.array([1, 0, 0, 1]) / np.sqrt(2)
    rho_target = np.outer(bell_state, bell_state)
    
    # Calculate Fidelity using PennyLane math
    fid = qml.math.fidelity(rho_out, rho_target)
    return 1 - fid  # We want to minimize cost, so maximize fidelity

if __name__ == "__main__":
    # Initialize random parameters
    params = np.random.normal(0, np.pi, 18, requires_grad=True)
    
    opt = qml.AdamOptimizer(stepsize=LEARNING_RATE)
    
    print(f"Starting Optimization (Noise = {NOISE_LEVEL*100}%)")
    print("-" * 40)
    
    for i in range(STEPS):
        params, cost = opt.step_and_cost(cost_fn, params)
        
        if i % 10 == 0:
            print(f"Step {i:3d} | Cost: {cost:.4f} | Fidelity: {(1-cost):.2%}")
            
    print("-" * 40)
    print("Optimization Complete!")
    print("\nOptimal Parameters found:")
    print(list(params.numpy()))
    print("\nCopy these parameters into src/protocol.py")