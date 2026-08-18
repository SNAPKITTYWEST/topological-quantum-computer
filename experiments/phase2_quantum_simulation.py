"""Phase 2: Quantum simulation on reduced-round SHA-520.

Success criteria:
- Toy SHA-520 (4-round, 16-bit) success rate > 90% on noiseless simulator
- With noise: success rate > 50%
- Circuit depth correlates with estimate ±20%
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "python"))

import json
from datetime import datetime


def run_phase2_simulation():
    """Simulate Grover on reduced-round SHA-520."""
    print("[Phase 2] Quantum Simulation (Reduced Rounds)")
    print("=" * 60)

    print("\n1. Attempting import of Qiskit...")
    try:
        from qiskit import QuantumCircuit, QuantumRegister
        print("   OK Qiskit available")
        has_qiskit = True
    except ImportError:
        print("   WARN Qiskit not available (optional dependency)")
        print("   Run: pip install qiskit qiskit-aer")
        has_qiskit = False

    print("\n2. Simulation configurations:")
    configs = [
        {"rounds": 4, "target_bits": 16, "name": "toy_4r_16b"},
        {"rounds": 4, "target_bits": 20, "name": "toy_4r_20b"},
        {"rounds": 8, "target_bits": 16, "name": "4r_16b"},
        {"rounds": 8, "target_bits": 24, "name": "8r_24b"},
    ]

    results = []
    for cfg in configs:
        print(f"   - {cfg['name']}: {cfg['rounds']}-round, {cfg['target_bits']}-bit target")

        if has_qiskit:
            result = {
                "config": cfg,
                "status": "NOT_EXECUTED_PLACEHOLDER",
                "evidence": "Qiskit is installed, but this phase script has not run the oracle simulator yet.",
                "circuit_depth": cfg['rounds'] * 2000 + cfg['target_bits'] * 100,
            }
        else:
            result = {
                "config": cfg,
                "status": "SKIPPED_NO_QISKIT",
                "reason": "Qiskit not installed"
            }
        results.append(result)

    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "phase": "2",
        "status": "SKIPPED_NO_QISKIT" if not has_qiskit else "PLACEHOLDER_ONLY",
        "qiskit_available": has_qiskit,
        "simulations": results,
        "total_configurations": len(results),
    }

    print("\n3. Report:")
    print(json.dumps(report, indent=2))

    output_file = Path(__file__).with_name("phase2_report.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n   OK Report saved to {output_file}")

    return report


if __name__ == "__main__":
    run_phase2_simulation()
