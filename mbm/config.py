from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_config(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_and_prepare(config: Dict[str, Any]) -> Tuple[
    int,                 # m (number of edges)
    int,                 # k
    Dict[str, Any],      # value_spec
    List[Dict[str, Any]],# weights_specs
    Dict[str, Any],      # budgets_cfg
    int | None,          # seed
    Dict[str, Any],      # graph_cfg
]:
    # Required: m (edges), k (dimensions), graph spec
    if "m" not in config or "k" not in config:
        raise ValueError("Config must contain 'm' (number of edges) and 'k' (number of dimensions).")
    m = int(config["m"])
    k = int(config["k"])
    if m <= 0 or k <= 0:
        raise ValueError("'m' and 'k' must be positive integers.")

    seed = config.get("seed", None)
    if seed is not None:
        seed = int(seed)

    value_spec = config.get("value", {"dist": "lognormal", "mean": 0.0, "sigma": 1.0, "min": 1.0})
    if not isinstance(value_spec, dict):
        raise ValueError("'value' must be a dict distribution spec.")

    weights_specs = config.get("weights", None)
    if weights_specs is None:
        weights_specs = [{"dist": "uniform", "low": 1.0, "high": 10.0} for _ in range(k)]
    if not (isinstance(weights_specs, list) and len(weights_specs) == k):
        raise ValueError(f"'weights' must be a list of length k={k} of per-dimension specs.")

    budgets_cfg = config.get("budgets", {})
    if not isinstance(budgets_cfg, dict):
        raise ValueError("'budgets' must be a dict with 'explicit' or 'fraction_of_sum'.")

    graph_cfg = config.get("graph", None)
    if not isinstance(graph_cfg, dict):
        raise ValueError("Config must contain a 'graph' dict with 'type' and size params.")
    gtype = graph_cfg.get("type", None)
    if gtype not in ("bipartite", "general"):
        raise ValueError("'graph.type' must be 'bipartite' or 'general'.")

    if gtype == "bipartite":
        if "num_left" not in graph_cfg or "num_right" not in graph_cfg:
            raise ValueError("'graph' for bipartite must specify 'num_left' and 'num_right'.")
        if int(graph_cfg["num_left"]) <= 0 or int(graph_cfg["num_right"]) <= 0:
            raise ValueError("'num_left' and 'num_right' must be positive.")
    else:
        if "num_vertices" not in graph_cfg or int(graph_cfg["num_vertices"]) < 2:
            raise ValueError("'graph' for general must specify 'num_vertices' >= 2.")

    return m, k, value_spec, weights_specs, budgets_cfg, seed, graph_cfg
