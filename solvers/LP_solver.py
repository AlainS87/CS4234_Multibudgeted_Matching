from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from mbm.types import MBMInstance, Edge
from .solver import Solver

# Try to import scipy linprog
try:
    from scipy.optimize import linprog
except Exception as e:
    raise ImportError("This LP solver needs scipy. Install via `pip install scipy`.") from e

class LPSolver(Solver):
    """
    LP relaxation for multi-budgeted matching (mBM).

    Variables:
        x_e in [0, 1] for each edge e.
    Constraints:
        For every vertex v: sum_{e incident to v} x_e <= 1
        For every budget dim j: sum_{e} w_e^{(j)} x_e <= B_j
    Objective:
        Maximize sum_e value_e * x_e  (converted to minimization of -value for linprog)
    """
        
    def __init__(self, instance: MBMInstance):
        super().__init__(instance)
        self.n = instance.num_vertices
        self.k = instance.k
        self.budgets = instance.budgets
        self.edges = instance.edges
        # basic checks
        if any(len(e.weights) != self.k for e in self.edges):
            raise ValueError("Each edge must carry k weights (one per budget dimension).")


    def solve(self,
                 method: str = "highs",
                 time_limit_s: Optional[float] = None) -> Dict[str, Any]:
        m = len(self.edges)
        # Objective: maximize c^T x  => minimize (-c)^T x
        c = -np.array([e.value for e in self.edges], dtype=float)

        # Build A_ub x <= b_ub
        rows = []
        rhs = []

        # (1) Vertex-degree constraints: for each vertex v, sum x_e (e incident to v) <= 1
        for v in range(self.n):
            row = np.zeros(m, dtype=float)
            for idx, e in enumerate(self.edges):
                if e.u == v or e.v == v:
                    row[idx] = 1.0
            rows.append(row)
            rhs.append(1.0)

        # (2) Budget constraints: for each j, sum w_e^{(j)} x_e <= B_j
        for j in range(self.k):
            row = np.array([e.weights[j] for e in self.edges], dtype=float)
            rows.append(row)
            rhs.append(self.budgets[j])

        A_ub = np.vstack(rows) if rows else None
        b_ub = np.array(rhs, dtype=float) if rhs else None

        # Bounds: 0 <= x_e <= 1
        bounds = [(0.0, 1.0) for _ in range(m)]

        # HiGHS options (optional time limit)
        options = {}
        if time_limit_s is not None:
            options["time_limit"] = float(time_limit_s)

        res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
                      method=method, options=options)

        out: Dict[str, Any] = {
            "ok": res.success,
            "status": res.status,
            "message": res.message,
            # LP relaxation objective value
            "lp_value": -res.fun if res.success and res.fun is not None else None,
            # Fractional solution values for x_e
            "x_frac": res.x if res.success else None,
        }

        # If successful, also provide per-edge fractionals and a simple rounding heuristic
        if res.success:
            edge_frac = []
            for i, e in enumerate(self.edges):
                edge_frac.append({
                    "index": i,
                    "u": e.u,
                    "v": e.v,
                    "value": e.value,
                    "weights": e.weights,
                    "x": float(res.x[i])
                })
            out["edge_fractionals"] = edge_frac

            # Simple greedy rounding: process edges in decreasing x_e order
            chosen = []
            used_v = np.zeros(self.n, dtype=bool)
            used_B = np.zeros(self.k, dtype=float)
            for i in np.argsort(-res.x):  # high to low
                e = self.edges[i]
                if used_v[e.u] or used_v[e.v]:
                    continue
                new_B = used_B + np.asarray(e.weights)
                if np.all(new_B <= np.asarray(self.budgets, dtype=float) + 1e-9):
                    chosen.append(i)
                    used_v[e.u] = True
                    used_v[e.v] = True
                    used_B = new_B
            int_value = sum(self.edges[i].value for i in chosen)
            out["rounded_indices"] = chosen
            out["rounded_value"] = int_value

        return res, out["rounded_value"], [(self.edges[i].u, self.edges[i].v) for i in out.get("rounded_indices", [])]