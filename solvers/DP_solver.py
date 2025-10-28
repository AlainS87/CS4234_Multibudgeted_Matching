# =============================================
# file: solver/DP_solver.py
# Exponential-in-n, pseudo-polynomial-in-budgets DP for small graphs
# =============================================
from __future__ import annotations
from typing import List, Tuple, Dict
from functools import lru_cache
from mbm.types import MBMInstance, Edge
from solvers.solver import Solver
import os

class DPSolver(Solver):
    """
    DP over vertex-mask and k-dimensional integer budgets.

    State: f(mask, b1, ..., bk) = max value using only vertices not in `mask` yet decided.
    Transition: pick the smallest free vertex u; either skip u, or match u with v>u (if edge exists),
    consuming the edge's k-dim budget. Returns optimal value and reconstructs chosen edges.

    Complexity: O(2^n * (n + m) * prod(b_d+1)) in worst case — only suitable for very small n
    (<= 22-ish with tiny budgets), but great as a correctness oracle and for unit tests.
    """

    def __init__(self, instance: MBMInstance):
        super().__init__(instance)
        self.n = instance.num_vertices
        self.k = instance.k
        self.budgets = instance.budgets
        # Build adjacency with edge attributes
        self.adj: Dict[int, List[Edge]] = {i: [] for i in range(self.n)}
        for e in instance.edges:
            if e.u == e.v:
                continue
            self.adj[e.u].append(e)
            self.adj[e.v].append(Edge(u=e.v, v=e.u, value=e.value, weights=e.weights))  # symmetric

    def solve(self) -> Tuple[int, List[Tuple[int, int]]]:
        # Sanity on budgets
        for w in self.budgets:
            if w < 0:
                raise ValueError("Budgets must be nonnegative integers")
        # lru_cache requires hashable budgets tuple; also keep them small
        max_mask = 1 << self.n

        @lru_cache(maxsize=None)
        def f(mask: int, *bs: int) -> int:
            # Find first free vertex u
            if mask == (1 << self.n) - 1:
                return 0
            u = (mask ^ ((1 << self.n) - 1)).bit_length() - 1  # highest free; we'll re-find properly
            # The above gives highest; we want smallest. Recompute plainly for clarity.
            for uu in range(self.n):
                if not (mask & (1 << uu)):
                    u = uu
                    break
            # Option 1: skip u (leave it unmatched)
            best = f(mask | (1 << u), *bs)
            # Option 2: match u with v via any available edge (u,v)
            for e in self.adj[u]:
                v = e.v
                if v <= u:
                    continue  # ensure each unordered pair once
                if mask & (1 << v):
                    continue  # v already taken
                ok = True
                new_bs = list(bs)
                for d in range(self.k):
                    if e.weights[d] > new_bs[d]:
                        ok = False
                        break
                    new_bs[d] -= e.weights[d]
                if not ok:
                    continue
                cand = e.value + f(mask | (1 << u) | (1 << v), *tuple(new_bs))
                if cand > best:
                    best = cand
            return best

        # Compute optimal value
        opt_val = f(0, *self.budgets)

        # Reconstruct chosen edges
        chosen: List[Tuple[int, int]] = []
        def reconstruct(mask: int, bs: Tuple[int, ...]):
            if mask == (1 << self.n) - 1:
                return
            # find smallest free u
            for uu in range(self.n):
                if not (mask & (1 << uu)):
                    u = uu
                    break
            # If skipping u preserves optimal value, do it
            if f(mask, *bs) == f(mask | (1 << u), *bs):
                reconstruct(mask | (1 << u), bs)
                return
            # Otherwise choose the matching edge that witnesses optimality
            current_best = f(mask, *bs)
            for e in self.adj[u]:
                v = e.v
                if v <= u or (mask & (1 << v)):
                    continue
                ok = True
                new_bs = list(bs)
                for d in range(self.k):
                    if e.weights[d] > new_bs[d]:
                        ok = False
                        break
                    new_bs[d] -= e.weights[d]
                if not ok:
                    continue
                vv = e.value + f(mask | (1 << u) | (1 << v), *tuple(new_bs))
                if vv == current_best:
                    chosen.append((u, v))
                    reconstruct(mask | (1 << u) | (1 << v), tuple(new_bs))
                    return
            # Should never fall through because skip already checked; but for safety
            reconstruct(mask | (1 << u), bs)

        reconstruct(0, self.budgets)
        return opt_val, chosen

# Allow `python -m solver.dp` to run on a default path
if __name__ == "__main__":
    import argparse
    from solvers.solver import Solver
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default=os.path.join("examples", "mbm_instance.json"),
                    help="Path to mBm instance JSON")
    args = ap.parse_args()
    inst = Solver.load_instance_from_json(args.instance)
    sol = DPSolver(inst)
    val, edges = sol.solve()
    print("Optimal value:", val)
    print("Chosen edges:", edges)
