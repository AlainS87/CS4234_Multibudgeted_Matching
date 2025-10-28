from pathlib import Path
import json
import sys

# Add the parent directory to Python path so we can import mbm
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mbm import mBm, load_config

if __name__ == "__main__":
    cfg_path = Path(__file__).parent.parent / "configs" / "sample_config.json"
    config = load_config(cfg_path)

    gen = mBm()
    inst = gen.generate_from_config(config)

    print("=== mBm Instance ===")
    print(f"graph_type = {inst.graph_type}")
    print(f"num_vertices = {inst.num_vertices}, |E| = {len(inst.edges)}, k = {inst.k}")
    if inst.graph_type == "bipartite":
        print(f"left = {inst.num_left}, right = {inst.num_right}")
    print("budgets:", inst.budgets)
    print("first 5 edges:", inst.edges[:5])

    out = Path(__file__).parent / "mbm_instance.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(inst.to_dict(), f, indent=2)
    print(f"\nWrote instance to: {out.resolve()}")
