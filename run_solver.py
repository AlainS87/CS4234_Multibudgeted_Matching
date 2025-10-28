# =============================================
# run_solver.py
# CLI wrapper to run different solvers (DP / LP) on mbm_instance.json
# =============================================
from __future__ import annotations
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import base Solver class
from solvers.solver import Solver

# Import specific solvers (you can extend this easily)
from solvers.DP_solver import DPSolver
from solvers.LP_solver import LPSolver


def main():
    parser = argparse.ArgumentParser(
        description="Run Multi-Budgeted Matching solvers on a JSON instance."
    )
    parser.add_argument(
        "--solver", "-s",
        choices=["dp", "lp"],
        default="dp",
        help="Solver to use: 'dp' (Dynamic Programming) or 'lp' (Linear Programming Relaxation)"
    )
    parser.add_argument(
        "--instance", "-i",
        default=os.path.join("examples", "mbm_instance.json"),
        help="Path to instance JSON file (default: examples/mbm_instance.json)"
    )

    args = parser.parse_args()

    # Load instance
    instance_path = args.instance
    if not os.path.exists(instance_path):
        print(f"[Error] Instance file not found: {instance_path}")
        sys.exit(1)

    inst = Solver.load_instance_from_json(instance_path)

    # Choose solver
    if args.solver == "dp":
        print("[INFO] Using DP solver.")
        solver = DPSolver(inst)
        print("[INFO] Running DP solver ...")
        opt_val, edges = solver.solve()
        print("Optimal value:", opt_val)
        print("Chosen edges (u, v):", edges)

    elif args.solver == "lp":
        if LPSolver is None:
            print("[Error] LP solver module not available.")
            sys.exit(1)

        print("[INFO] Running LP solver (relaxation) ...")
        solver = LPSolver(inst)
        res, opt_val, edges = solver.solve()
        print("LP success:", "Yes" if res["success"] else "No")
        print("LP upper bound value:", -res["fun"])
        print("Rounded integer value (heuristic):", opt_val)
        print("Chosen edges:", edges)

    else:
        print(f"[Error] Unknown solver type: {args.solver}")
        sys.exit(1)


if __name__ == "__main__":
    main()
