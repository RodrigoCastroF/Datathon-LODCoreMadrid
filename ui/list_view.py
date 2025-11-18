# ui/list_view.py
"""List view with municipality cards."""

import math
from typing import Dict, Optional

import pandas as pd
import streamlit as st
from PIL import Image


def render_municipality_card(muni: pd.Series, images: Dict[str, Optional[Image.Image]]) -> None:
    """Render single municipality card.
    
    Args:
        muni: Municipality data series
        images: Dictionary of placeholder images (unused, kept for compatibility)
    """
    st.markdown('<div class="municipality-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        from core.data_loader import get_municipality_image
        img = get_municipality_image(muni["Nombre"])
        if img:
            st.image(img, width='stretch')

    with col2:
        st.markdown(f"<div class='municipality-name'>{muni['Nombre']}</div>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="score-badge">Puntuación: {muni["weighted_score"]:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            (
                f"👥 **Población:** {int(muni['IDE_PoblacionTotal']):,}<br>"
                f"💰 **Precio vivienda:** {muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²<br>"
                f"⌛ **Horas al mes en transporte:** {muni['AccessibilityHoursMonthly']:.1f}"
            ),
            unsafe_allow_html=True,
        )

        if st.button("Ver detalles", key=f"details_btn_{muni['codigo']}"):
            st.session_state["selected_municipality"] = muni
            st.session_state["details_origin"] = "list"
            st.session_state["suppress_map_selection"] = True
            st.session_state["switch_view_to"] = "📋 Lista de municipios"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ui/list_view.py - Replace render_list_view function

def render_list_view(scores_df: pd.DataFrame, images: Dict[str, Optional[Image.Image]]) -> None:
    """Render paginated list of municipalities.
    
    Args:
        scores_df: Sorted DataFrame with municipality scores
        images: Dictionary of placeholder images (unused, kept for compatibility)
    """
    if len(scores_df) == 0:
        st.info("No hay municipios disponibles para mostrar.")
        return

    st.markdown("### 📋 Municipios ordenados por puntuación")

    page_size = 10
    total = len(scores_df)
    num_pages = max(1, math.ceil(total / page_size))

    page = st.number_input(
        "Página",
        min_value=1,
        max_value=num_pages,
        value=st.session_state.get("list_page", 1),
        step=1,
        key="list_page",
    )

    start = (page - 1) * page_size
    end = start + page_size
    page_df = scores_df.iloc[start:end]

    for _, row in page_df.iterrows():
        render_municipality_card(row, images)
        
        # Show details inline if this municipality is selected
        if ("selected_municipality" in st.session_state and 
            st.session_state.get("details_origin") == "list" and
            st.session_state["selected_municipality"]["codigo"] == row["codigo"]):
            st.markdown("---")
            from ui.details_view import render_details
            render_details(st.session_state["selected_municipality"], images, scores_df)
            st.markdown("---")

