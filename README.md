# 🧩 Multi-Budgeted Matching (mBM) Solver

This project provides a modular Python framework for **multi-budgeted matching (mBM)** —  
a generalization of maximum matching with multiple resource (budget) constraints.

It supports:
- Random instance generation via configuration files  
- Multiple solvers (Dynamic Programming, LP relaxation, etc.)  
- A simple command-line interface for running experiments and measuring runtime

---

## 📂 Project Structure

```
CS4234_Multibudgeted_Matching/
├── README.md
│
├── configs/
│   └── mbm_instance_config.json          # Configuration for instance generation
│
├── examples/
│   ├── demo_generate.py            # Generate random mBM instances
│   └── mbm_instance.json           # Example generated instance
│
├── mbm/
│   ├── __init__.py
│   ├── config.py                   # Load and parse configuration files
│   ├── generator.py                # Generate random mBM instances
│   ├── types.py                    # Data structures (Edge, Instance, etc.)
│   └── utils.py                    # Helper utilities
│
├── solvers/
│   ├── solver.py                   # Base Solver interface + instance loader
│   ├── DP_solver.py                # Dynamic Programming solver (exact)
│   ├── LP_solver.py                # LP relaxation solver (fractional)
│   └── __pycache__/                # Compiled Python cache
│
├── run_solver.py                   # CLI wrapper for solver execution
│
└── test/
    └── solve_dp.py                 # Unit test / example script for DP solver
```
---

## 🚀 Quick Start (in Codespaces or locally)

### 1️⃣ Environment Setup
Make sure you have Python 3.9+ and install dependencies:

```bash
pip install -r requirements.txt
```

or minimal setup:

```bash
pip install numpy scipy
```

---

### 2️⃣ Generate an mBM Instance

Generate a random instance according to `configs/mbm_instance_config.json`:

```bash
python examples/demo_generate.py
```

This creates `examples/mbm_instance.json` containing:
- Graph type (bipartite or general)
- Number of vertices
- Edge values and multi-dimensional weights
- Budget constraints per dimension

---

### 3️⃣ Solve the Instance

You can choose different solvers:

#### 🧮 Dynamic Programming (DP)
```bash
python run_solver.py --solver dp
```

#### 🧩 Linear Programming (LP Relaxation)
```bash
python run_solver.py --solver lp
```

You can extend `run_solver.py` with other solvers as needed.

---

### 4️⃣ Example Output

```text
[INFO] Running LP solver (relaxation) ...
LP success: True
LP upper bound (maximize): 313.0952
Heuristic rounded integer value: 297.0
Chosen edges (u, v): [(0, 3), (1, 4), (2, 5)]
Runtime: 0.012s
```

or for the DP solver:

```text
[INFO] Running DP solver ...
Optimal value: 310.0
Chosen edges (u, v): [(0, 2), (3, 5), (4, 6)]
Runtime: 0.45s
```

---

## 🧠 Notes

- **LP solver** uses SciPy’s `linprog` (`method="highs"`) to solve LP relaxations.  
  It outputs fractional solutions and applies a simple greedy rounding heuristic.  
- **DP solver** is exact but slower for large instances.  
- Both solvers print runtime; this can be extended for benchmarking.

---

## 🧩 Extending the Project

To add a new solver:
1. Create `solvers/MySolver.py`
2. Implement a subclass of `Solver` with a `solve()` method
3. Register it in `run_solver.py` (e.g., add `--solver mysolver`)

---

## 🧑‍💻 Example Workflow (Codespaces)

```bash
# Step 1: Generate an instance
python examples/demo_generate.py

# Step 2: Solve using LP relaxation
python run_solver.py --solver lp

# Step 3: Solve using Dynamic Programming
python run_solver.py --solver dp
```

---

## 📘 Reference

This project is part of **CS4234 — Advanced Algorithms** (NUS, 2025),  
focusing on **multi-budgeted matching** and resource-constrained optimization.

---

## 🪶 Author
**Alain Su**  
CS4234: Advanced Algorithms — NUS 2025

## Appendix:  ⚙️ Configuration File (`configs/sample_config.json`)

The configuration file defines how random mBM instances are generated.  
It controls the number of vertices, budgets, graph type, and distributions of edge values and weights.

Below is the general format:

```json
{
  "graph_type": "bipartite",
  "num_left": 7,
  "num_right": 7,
  "num_edges": 30,
  "k": 3,
  "budgets": [20.0, 25.0, 15.0],
  "value": {
    "dist": "lognormal",
    "mean": 3.0,
    "sigma": 1.0,
    "min": 1.0
  },
  "weights": [
    {"dist": "uniform", "low": 1.0, "high": 10.0},
    {"dist": "uniform", "low": 1.0, "high": 10.0},
    {"dist": "uniform", "low": 1.0, "high": 10.0}
  ]
}
```

### 🔹 Parameter Details

| Key | Type | Description |
|-----|------|--------------|
| **graph_type** | `"bipartite"` or `"general"` | Type of graph to generate. `bipartite` creates two disjoint vertex sets (left/right). |
| **num_left**, **num_right** | `int` | Number of vertices on each side (for bipartite). |
| **num_vertices** | `int` | (Alternative for `general` graphs) total number of vertices. |
| **num_edges** | `int` | Number of edges to sample randomly. |
| **k** | `int` | Number of budget dimensions (constraints). |
| **budgets** | `list[float]` | Total budget for each dimension \( B_1, B_2, \dots, B_k \). |
| **value** | `dict` | Distribution of edge values (objective coefficients). Supports fields: <br>• `"dist"`: distribution name (`"uniform"`, `"normal"`, `"lognormal"`, etc.) <br>• `"mean"`, `"sigma"`, `"low"`, `"high"` depending on dist <br>• `"min"`: lower bound cutoff. |
| **weights** | `list[dict]` | A list of *k* independent weight specifications (one per budget). <br>Each dict follows same pattern as `"value"`. |

---

### 🧮 Example Interpretations

- `"graph_type": "bipartite"`  
  → generator builds a bipartite graph with `num_left × num_right` possible edges.

- `"k": 3`, `"budgets": [20,25,15]`  
  → you have 3 resource constraints; each edge has 3 weights `[w₁,w₂,w₃]`,  
  and the sum over chosen edges must not exceed each budget.

- `"value": {"dist": "lognormal", "mean": 3.0, "sigma": 1.0}`  
  → edge values are drawn from a lognormal distribution (shifted/scaled).

- `"weights": [{"dist":"uniform","low":1,"high":10}, ...]`  
  → each dimension’s edge weight is sampled independently between 1–10.

---

### 🧩 Extending Configuration

You can easily add new distributions or parameters:
- Add support for `"normal"`, `"exponential"`, etc. in `mbm/generator.py`.
- You can also fix certain weights or budgets by setting explicit constants:
  ```json
  "weights": [{"dist": "constant", "value": 5.0}, ...]
  ```
- To reproduce experiments, set a fixed random seed:
  ```json
  "seed": 42
  ```

---
