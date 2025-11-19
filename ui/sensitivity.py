# ui/sensitivity.py
"""Sensitivity analysis component."""

from typing import Dict, List

import pandas as pd
import streamlit as st

from config.constants import CRITERIA_LABELS


def perturb_weights(weights: Dict[str, float], targets: List[str], delta: float) -> Dict[str, float]:
    """Perturb weights by delta and renormalize.
    
    Args:
        weights: Original weights
        targets: Criteria to perturb
        delta: Relative change (e.g., 0.10 for +10%)
        
    Returns:
        Perturbed and renormalized weights
    """
    w2 = {k: v * (1 + delta if k in targets else 1) for k, v in weights.items()}
    total = sum(w2.values())
    return {k: v / total for k, v in w2.items()}


def render_sensitivity(scores_df: pd.DataFrame, weights: Dict[str, float], norm_df: pd.DataFrame, compute_scores_fn) -> None:
    """Render sensitivity analysis expander.
    
    Args:
        scores_df: Base scores DataFrame
        weights: Current weights
        norm_df: Normalized data
        compute_scores_fn: Function to recompute scores
    """
    if len(scores_df) == 0:
        return

    with st.expander(":material/science: | Análisis de sensibilidad", expanded=False):
        st.markdown("**¿Qué pasa si cambio ligeramente mis prioridades?**")
        st.caption("Variamos los 3 criterios más importantes ±10% para ver si el ranking cambia mucho.")

        top3 = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_names = [k for k, _ in top3]
        st.write(f"**Criterios variados:** {', '.join([CRITERIA_LABELS[k] for k in top3_names])}")

        w_plus = perturb_weights(weights, top3_names, 0.10)
        w_minus = perturb_weights(weights, top3_names, -0.10)

        scores_plus = compute_scores_fn(norm_df, w_plus)
        scores_minus = compute_scores_fn(norm_df, w_minus)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Pesos base**")
            st.dataframe(scores_df[["Nombre", "weighted_score"]].head(10), hide_index=True, width='stretch')
        with col2:
            st.markdown("**Pesos +10%**")
            st.dataframe(scores_plus[["Nombre", "weighted_score"]].head(10), hide_index=True, width='stretch')
        with col3:
            st.markdown("**Pesos -10%**")
            st.dataframe(scores_minus[["Nombre", "weighted_score"]].head(10), hide_index=True, width='stretch')

        top5_base = set(scores_df.head(5)["Nombre"].tolist())
        top5_plus = set(scores_plus.head(5)["Nombre"].tolist())
        top5_minus = set(scores_minus.head(5)["Nombre"].tolist())

        overlap_plus = len(top5_base & top5_plus)
        overlap_minus = len(top5_base & top5_minus)

        st.markdown("---\n**:material/analytics: Estabilidad del Top-5:**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Coincidencia con +10%", f"{overlap_plus}/5", delta="Estable" if overlap_plus >= 4 else "Variable")
        with col_b:
            st.metric("Coincidencia con -10%", f"{overlap_minus}/5", delta="Estable" if overlap_minus >= 4 else "Variable")

        if overlap_plus >= 4 and overlap_minus >= 4:
            st.success(":material/check: Ranking muy estable. Tus preferencias producen resultados robustos.")
        elif overlap_plus >= 3 and overlap_minus >= 3:
            st.info(":material/info: Ranking moderadamente estable. Pequeños cambios afectan algo el orden.")
        else:
            st.warning(":material/warning: Ranking sensible. Considera ajustar tus prioridades para mayor claridad.")
