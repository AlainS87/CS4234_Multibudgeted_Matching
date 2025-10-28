# =============================================
# file: solver/base.py
# Base classes and utilities for mBm solvers
# =============================================
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
from mbm.types import MBMInstance, Edge
import json
import os

class Solver:
    """Abstract base class for mBm solvers.

    Subclasses must implement `solve()` and return (opt_value, chosen_edges_list)
    where chosen_edges_list is a list of (u, v) pairs (ints).
    """
    def __init__(self, instance: MBMInstance):
        self.instance = instance

    def solve(self) -> Tuple[int, List[Tuple[int, int]]]:
        raise NotImplementedError

    # ----------------------
    # Helper: load instance
    # ----------------------
    @staticmethod
    def load_instance_from_json(path: str) -> MBMInstance:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Instance file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Flexible schema handling
        # Expected keys (any reasonable variant supported):
        #   n: int
        #   k: int (optional if inferable from edge weights)
        #   budgets / W / capacities: list[int]
        #   edges: list of {u, v, value/val/w, weights/costs}
        #   graph_type: optional
        n: Optional[int] = data.get("n")
        graph_type = data.get("graph_type", data.get("type", "general"))
        budgets_key = next((k for k in ("budgets", "W", "capacities") if k in data), None)
        if budgets_key is None:
            raise ValueError("Missing 'budgets' (or 'W'/'capacities') in instance JSON")
        budgets_list = data[budgets_key]
        budgets = tuple(int(x) for x in budgets_list)
        edges_raw = data.get("edges")
        if not isinstance(edges_raw, list) or not edges_raw:
            raise ValueError("'edges' must be a non-empty list")
        edges: List[Edge] = []
        inferred_k: Optional[int] = None
        max_vertex = -1
        for e in edges_raw:
            u = int(e.get("u"))
            v = int(e.get("v"))
            val_key = next((k for k in ("value", "val", "w") if k in e), None)
            if val_key is None:
                raise ValueError("Edge is missing 'value' (or 'val'/'w')")
            value = int(e[val_key])
            weights_key = next((k for k in ("weights", "costs") if k in e), None)
            if weights_key is None:
                raise ValueError("Edge is missing 'weights' (or 'costs')")
            weights_list = e[weights_key]
            if inferred_k is None:
                inferred_k = len(weights_list)
            elif inferred_k != len(weights_list):
                raise ValueError("Inconsistent weight dimensions among edges")
            weights = tuple(int(x) for x in weights_list)
            edges.append(Edge(u=u, v=v, value=value, weights=weights))
            max_vertex = max(max_vertex, u, v)
        if n is None:
            n = max_vertex + 1
        if inferred_k is None:
            inferred_k = len(budgets)
        k = data.get("k", inferred_k)
        if k != len(budgets):
            raise ValueError(f"k={k} but len(budgets)={len(budgets)} mismatch")
        for e in edges:
            if len(e.weights) != k:
                raise ValueError("Each edge weight vector must have length k")
        return MBMInstance(num_vertices=n, k=k, budgets=budgets, edges=edges, graph_type=graph_type)
