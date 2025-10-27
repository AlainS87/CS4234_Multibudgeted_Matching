from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Literal, Optional


GraphType = Literal["bipartite", "general"]


@dataclass
class MBMInstance:
    """
    A multi-budget matching (mBm) instance with an explicit graph.

    Attributes
    ----------
    graph_type : "bipartite" | "general"
        Graph category.
    num_vertices : int
        Total number of vertices in the graph.
    num_left : Optional[int]
        For bipartite graphs: size of the left partition U. None for general graphs.
    num_right : Optional[int]
        For bipartite graphs: size of the right partition V. None for general graphs.
    edges : List[Tuple[int, int]]
        List of undirected edges (u, v) with 0 <= u < v < num_vertices.
        For bipartite graphs: u in [0, num_left), v in [num_left, num_left+num_right).
    k : int
        Number of budget dimensions.
    values : List[float]
        Per-edge value; len(values) == len(edges).
    weights : List[List[float]]
        Shape m x k, where m = len(edges). weights[e][t] is cost of edge e on dim t.
    budgets : List[float]
        Length-k budgets (capacities) — sum of chosen edges' weights must not exceed these.
    """
    graph_type: GraphType
    num_vertices: int
    edges: List[Tuple[int, int]]
    k: int
    values: List[float]
    weights: List[List[float]]
    budgets: List[float]
    num_left: Optional[int] = None
    num_right: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_type": self.graph_type,
            "num_vertices": self.num_vertices,
            "num_left": self.num_left,
            "num_right": self.num_right,
            "edges": self.edges,
            "k": self.k,
            "values": self.values,
            "weights": self.weights,
            "budgets": self.budgets,
        }
