# =============================================
# Small CLI convenience wrapper to run the DP solver on examples/mbm_instance.json
# =============================================
# Add the parent directory to Python path so we can import mbm
from __future__ import annotations
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solvers.solver import Solver
from solvers.DP_solver import DPSolver
import os

def main():
    instance_path = os.path.join("examples", "mbm_instance.json")
    inst = Solver.load_instance_from_json(instance_path)
    solver = DPSolver(inst)
    opt_val, edges = solver.solve()
    print("Optimal value:", opt_val)
    print("Chosen edges (u, v):", edges)

if __name__ == "__main__":
    main()