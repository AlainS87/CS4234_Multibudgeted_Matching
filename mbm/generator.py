from __future__ import annotations
import random
from typing import Any, Dict, List, Tuple, Set

from .types import MBMInstance, GraphType
from .utils import sample_one, distribution_expectation
from .config import validate_and_prepare


class mBm:
    """
    mBm generator (graph-based).
    """

    def __init__(self) -> None:
        pass

    # ---- budgets ----
    def _compute_budgets(
        self,
        m: int,
        k: int,
        weights: List[List[float]],
        weights_specs: List[Dict[str, Any]],
        budgets_cfg: Dict[str, Any],
    ) -> List[float]:
        if "explicit" in budgets_cfg and budgets_cfg["explicit"] is not None:
            explicit = budgets_cfg["explicit"]
            if not (isinstance(explicit, list) and len(explicit) == k):
                raise ValueError(f"'budgets.explicit' must be a list of length k={k}.")
            return [float(x) for x in explicit]

        frac = float(budgets_cfg.get("fraction_of_sum", 0.6))
        if not (0.0 < frac <= 1.5):
            raise ValueError("'fraction_of_sum' must be in (0, 1.5].")

        budgets: List[float] = []
        for t in range(k):
            exp_t = distribution_expectation(weights_specs[t])
            if exp_t is not None:
                total = m * exp_t
            else:
                total = sum(weights[e][t] for e in range(m))
            budgets.append(frac * total)
        return budgets

    # ---- edges ----
    def _gen_edges_bipartite(self, num_left: int, num_right: int, m: int) -> Tuple[int, List[Tuple[int, int]]]:
        """
        Return (num_vertices, edges). Vertices: [0..num_left-1] U [num_left..num_left+num_right-1].
        Edges are unique pairs (u in left, v in right) with u < v in numeric label after shift.
        """
        total_v = num_left + num_right
        edges: List[Tuple[int, int]] = []
        used: Set[Tuple[int, int]] = set()

        # Sample without parallel edges or self-loops.
        while len(edges) < m:
            u = random.randrange(0, num_left)
            v = num_left + random.randrange(0, num_right)
            e = (u, v) if u < v else (v, u)
            if e not in used:
                used.add(e)
                edges.append(e)

        return total_v, edges

    def _gen_edges_general(self, num_vertices: int, m: int) -> List[Tuple[int, int]]:
        """
        Return a list of m unique undirected edges (u, v), u < v, no self-loops, no parallel edges.
        """
        if m > num_vertices * (num_vertices - 1) // 2:
            raise ValueError("Too many edges requested for a simple graph without parallel edges.")

        edges: List[Tuple[int, int]] = []
        used: Set[Tuple[int, int]] = set()

        while len(edges) < m:
            u = random.randrange(0, num_vertices)
            v = random.randrange(0, num_vertices)
            if u == v:
                continue
            a, b = (u, v) if u < v else (v, u)
            if (a, b) in used:
                continue
            used.add((a, b))
            edges.append((a, b))

        return edges

    # ---- main ----
    def generate_from_config(self, config: Dict[str, Any]) -> MBMInstance:
        """
        Generate one mBm instance with per-edge attributes:
        edges: [ {"u": int, "v": int, "value": float, "weights": [float, ...]}, ... ]
        Other top-level fields:
        graph_type, num_vertices, num_left/num_right (if bipartite), k, budgets
        """
        m, k, value_spec, weights_specs, budgets_cfg, seed, graph_cfg = validate_and_prepare(config)
        if seed is not None:
            random.seed(seed)

        gtype: GraphType = graph_cfg["type"]  # validated
        if gtype == "bipartite":
            L = int(graph_cfg["num_left"])
            R = int(graph_cfg["num_right"])
            num_vertices, edge_pairs = self._gen_edges_bipartite(L, R, m)  # [(u,v)]
            num_left, num_right = L, R
        else:
            V = int(graph_cfg["num_vertices"])
            edge_pairs = self._gen_edges_general(V, m)  # [(u,v)]
            num_vertices = V
            num_left = num_right = None  # not applicable

        # --- Sample per-edge value and k-dim weights ---
        values: List[float] = [float(sample_one(value_spec)) for _ in range(m)]
        weights: List[List[float]] = [
            [float(sample_one(weights_specs[t])) for t in range(k)]
            for _ in range(m)
        ]

        # --- Budgets from weights (same as before) ---
        budgets = self._compute_budgets(m, k, weights, weights_specs, budgets_cfg)

        # --- Assemble per-edge dicts: {"u","v","value","weights"} ---
        edges_attrs: List[Dict[str, Any]] = []
        for i, (u, v) in enumerate(edge_pairs):
            edges_attrs.append({
                "u": int(u),
                "v": int(v),
                "value": values[i],
                "weights": [float(w) for w in weights[i]],
            })

        # --- Return MBMInstance (edges now carry attributes) ---
        return MBMInstance(
            graph_type=gtype,
            num_vertices=num_vertices,
            num_left=num_left,
            num_right=num_right,
            edges=edges_attrs,   # ← 这里现在是 per-edge dict 列表
            k=k,
            budgets=budgets,     # 顶层仍保留 budgets
        )


    def generate_from_file(self, path: str) -> MBMInstance:
        from .config import load_config
        cfg = load_config(path)
        return self.generate_from_config(cfg)
