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
                f":material/group: **Población:** {int(muni['IDE_PoblacionTotal']):,}<br>"
                f":material/payments: **Precio vivienda:** {muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²<br>"
                f":material/schedule: **Horas al mes en transporte:** {muni['AccessibilityHoursMonthly']:.1f}"
            ),
            unsafe_allow_html=True,
        )

        if st.button("Ver detalles", key=f"details_btn_{muni['codigo']}"):
            st.session_state["selected_municipality"] = muni
            st.session_state["details_origin"] = "list"
            st.session_state["suppress_map_selection"] = True
            st.session_state["switch_view_to"] = ":material/list: Lista de municipios"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_pagination(current_page: int, num_pages: int, key_suffix: str) -> None:
    """Render pagination controls.
    
    Args:
        current_page: Current page number
        num_pages: Total number of pages
        key_suffix: Unique suffix for button keys
    """
    col_prev, col_info, col_next = st.columns([1, 14, 1])
    
    with col_prev:
        if st.button("←", disabled=(current_page <= 1), key=f"prev_{key_suffix}"):
            st.session_state["list_page"] = current_page - 1
            st.rerun()
    
    with col_info:
        st.markdown(
            f"<div style='text-align: center; padding: 0.5rem;'>Página {current_page} de {num_pages}</div>",
            unsafe_allow_html=True
        )
    
    with col_next:
        if st.button("→", disabled=(current_page >= num_pages), key=f"next_{key_suffix}"):
            st.session_state["list_page"] = current_page + 1
            st.rerun()


def render_list_view(scores_df: pd.DataFrame, images: Dict[str, Optional[Image.Image]]) -> None:
    """Render paginated list of municipalities with arrow navigation.
    
    Args:
        scores_df: Sorted DataFrame with municipality scores
        images: Dictionary of placeholder images (unused, kept for compatibility)
    """
    if len(scores_df) == 0:
        st.info("No hay municipios disponibles para mostrar.")
        return

    st.markdown("### :material/list: Municipios ordenados por puntuación")
    st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)


    page_size = 10
    total = len(scores_df)
    num_pages = max(1, math.ceil(total / page_size))
    
    # Initialize page in session state
    if "list_page" not in st.session_state:
        st.session_state["list_page"] = 1
    
    current_page = st.session_state["list_page"]

    # Top pagination
    _render_pagination(current_page, num_pages, "top")
    st.markdown('<hr style="margin: -0.3rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)


    # Render municipality cards
    start = (current_page - 1) * page_size
    end = start + page_size
    page_df = scores_df.iloc[start:end]

    for _, row in page_df.iterrows():
        render_municipality_card(row, images)
        
        # Show details inline if this municipality is selected
        if ("selected_municipality" in st.session_state and 
            st.session_state.get("details_origin") == "list" and
            st.session_state["selected_municipality"]["codigo"] == row["codigo"]):
            st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)
            from ui.details_view import render_details
            render_details(st.session_state["selected_municipality"], images, scores_df)
            st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)


    # Bottom pagination
    st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)

    _render_pagination(current_page, num_pages, "bottom")
