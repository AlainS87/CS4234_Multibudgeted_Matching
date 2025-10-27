from __future__ import annotations
import math
import random
from typing import Any, Dict, Optional


def clip(x: float, lo: Optional[float], hi: Optional[float]) -> float:
    if lo is not None:
        x = max(x, float(lo))
    if hi is not None:
        x = min(x, float(hi))
    return x


def sample_one(spec: Dict[str, Any]) -> float:
    d = spec.get("dist", "uniform")

    if d == "uniform":
        a = float(spec.get("low", 0.0))
        b = float(spec.get("high", 1.0))
        x = random.uniform(a, b)

    elif d == "int_uniform":
        a = int(spec.get("low", 0))
        b = int(spec.get("high", 10))
        x = float(random.randint(a, b))

    elif d == "normal_pos":
        mean = float(spec.get("mean", 1.0))
        std = float(spec.get("std", 1.0))
        while True:
            x = random.gauss(mean, std)
            if x > 0:
                break

    elif d == "lognormal":
        mu = float(spec.get("mean", 0.0))
        sigma = float(spec.get("sigma", 1.0))
        x = random.lognormvariate(mu, sigma)

    else:
        raise ValueError(f"Unsupported distribution: {d}")

    return clip(x, spec.get("min"), spec.get("max"))


def distribution_expectation(spec: Dict[str, Any]) -> Optional[float]:
    if spec.get("min") is not None or spec.get("max") is not None:
        return None

    d = spec.get("dist", "uniform")
    if d == "uniform":
        a = float(spec.get("low", 0.0))
        b = float(spec.get("high", 1.0))
        return 0.5 * (a + b)

    if d == "int_uniform":
        a = int(spec.get("low", 0))
        b = int(spec.get("high", 10))
        return 0.5 * (a + b)

    if d == "lognormal":
        mu = float(spec.get("mean", 0.0))
        sigma = float(spec.get("sigma", 1.0))
        return math.exp(mu + 0.5 * sigma * sigma)

    return None
