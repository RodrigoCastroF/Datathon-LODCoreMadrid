# core/scoring.py
"""Normalization and scoring functions for municipality ranking."""

import numpy as np
import pandas as pd
from typing import Dict


def normalize_criteria(
    df: pd.DataFrame,
    benefit_cols: Dict[str, str],
    cost_cols: Dict[str, str],
    accessibility_col: str = "AccessibilityHoursWeekly",
) -> pd.DataFrame:
    """Normalize all criteria to [0,1] with higher=better.
    
    Benefit criteria: (x - min) / (max - min)
    Cost criteria: 1 - (x - min) / (max - min)
    
    Args:
        df: Municipality dataset
        benefit_cols: Mapping {criterion: column_name} for benefits
        cost_cols: Mapping {criterion: column_name} for costs
        accessibility_col: Name of accessibility hours column
        
    Returns:
        DataFrame with NORM_{criterion} columns added
    """
    out = df.copy()

    # Normalize benefits (higher is better)
    for crit, col in benefit_cols.items():
        x = out[col].astype(float)
        rng = x.max() - x.min()
        out[f"NORM_{crit}"] = (x - x.min()) / (rng if rng != 0 else 1.0)

    # Normalize costs (lower is better → invert)
    xp = out[cost_cols["HousePriceSqm"]].astype(float)
    prng = xp.max() - xp.min()
    out["NORM_HousePriceSqm"] = 1.0 - (xp - xp.min()) / (prng if prng != 0 else 1.0)

    xa = out[accessibility_col].astype(float)
    arng = xa.max() - xa.min()
    out["NORM_AccessibilityHoursWeekly"] = 1.0 - (xa - xa.min()) / (arng if arng != 0 else 1.0)

    return out


def compute_scores(df_norm: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    """Compute weighted scores and rank municipalities.
    
    Args:
        df_norm: Normalized dataset with NORM_{criterion} columns
        weights: Mapping {criterion: weight} (should sum to 1)
        
    Returns:
        Sorted DataFrame with Score, weighted_score, and CONTRIB_{criterion} columns
    """
    out = df_norm.copy()
    score = np.zeros(len(out), dtype=float)

    for crit, w in weights.items():
        w = float(w)
        col = f"NORM_{crit}"
        contrib = w * out[col].astype(float)
        out[f"CONTRIB_{crit}"] = contrib
        score += contrib.values

    out["Score"] = score
    max_score = out["Score"].max()
    out["weighted_score"] = (out["Score"] / max_score * 100.0) if max_score > 0 else 0.0
    return out.sort_values("Score", ascending=False).reset_index(drop=True)


def equal_weights(criteria: list) -> Dict[str, float]:
    """Generate equal weights for all criteria.
    
    Args:
        criteria: List of criterion names
        
    Returns:
        Dictionary with equal weights summing to 1
    """
    w = 1.0 / len(criteria)
    return {c: w for c in criteria}
