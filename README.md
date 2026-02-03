# Dufresne Protocol: Variational Entanglement Purification

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-experimental-orange)
![Platform](https://img.shields.io/badge/platform-IBM%20Quantum-purple)

## 📄 Abstract

This repository contains the source code and experimental data for the **Dufresne Protocol**, a Variational Quantum Circuit (VQC) designed to purify Bell pairs on noisy superconducting quantum processors.

Unlike standard purification protocols (e.g., BBPSSW) which rely on fixed CNOT gates, this approach uses an 18-parameter ansatz optimized via hybrid classical-quantum learning. It is designed to adapt to hardware-specific noise profiles (crosstalk, calibration errors) inherent to the NISQ era.

**Key Experimental Result:** Tested on the 127-qubit **IBM Eagle processor** (`ibm_fez`), the protocol achieved a post-distillation fidelity of **96.38%** (vs 95.70% for the standard protocol), representing a **15.8% relative reduction in error rate**.

---

## 📂 Repository Structure

```text
dufresne-quantum-protocol/
├── src/                  # The core Python package
│   └── protocol.py       # The optimized DufresneProtocol class
├── experiments/          # Reproducible scripts
│   ├── 01_optimization.py  # VQC Training script (Simulator)
│   └── 02_ibm_benchmark.py # Real hardware benchmark script
├── paper/                # Scientific Paper (PDF & LaTeX)
├── figures/              # High-resolution plots
└── requirements.txt      # Dependencies

```

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/ton-pseudo/dufresne-quantum-protocol.git](https://github.com/ton-pseudo/dufresne-quantum-protocol.git)
cd dufresne-quantum-protocol

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Environment Setup (Important):**
Create a `.env` file at the root of the project to store your IBM Quantum API token safely:
```ini
IBM_QUANTUM_TOKEN=your_ibm_token_here

```



---

## 💻 Usage

### 1. Using the Protocol in your own circuits

You can import the pre-optimized protocol directly from the source:

```python
import pennylane as qml
from src.protocol import DufresneProtocol

# Initialize the protocol (loads the 18 optimized parameters)
protocol = DufresneProtocol()

dev = qml.device('default.mixed', wires=4)

@qml.qnode(dev)
def my_circuit():
    # ... State preparation ...
    
    # Apply the Dufresne Purification
    protocol.apply(wires_alice=[0, 2], wires_bob=[1, 3])
    
    return qml.probs(wires=[0, 1])

```

### 2. Running the Benchmark (Real Hardware)

To reproduce the paper's results on IBM Quantum:

```bash
python experiments/02_ibm_benchmark.py

```

*Note: This requires an active IBM Quantum account with access to Eagle processors.*

---

## 📊 Results & Performance

### Circuit Architecture

The ansatz introduces parameterized rotation layers  before and after the distillation logic to correct basis misalignment.

### Benchmark on IBM Eagle

The variational approach significantly suppresses the residual error rate compared to the standard BBPSSW protocol.

---

## 📝 Citation

If you use this code or data in your research, please cite:

```bibtex
@article{dufresne2026,
  title={Experimental Demonstration of Variational Entanglement Purification on Superconducting Qubits},
  author={Dufresne, Martin},
  year={2026},
  publisher={GitHub},
  journal={GitHub Repository},
  url={[https://github.com/ton-pseudo/dufresne-quantum-protocol](https://github.com/ton-pseudo/dufresne-quantum-protocol)}
}

```

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/MIT) file for details.