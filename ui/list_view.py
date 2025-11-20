# ui/list_view.py
"""List view with municipality cards."""

import math
from typing import Dict, Optional

import pandas as pd
import streamlit as st
from PIL import Image


def render_municipality_card(muni: pd.Series, images: Dict[str, Optional[Image.Image]], row_idx: int) -> None:
    """Render single municipality card.
    
    Args:
        muni: Municipality data series
        images: Dictionary of placeholder images (unused, kept for compatibility)
        row_idx: Unique row index to prevent duplicate keys
    """
    st.markdown('<div class="municipality-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        from core.data_loader import get_municipality_image
        img = get_municipality_image(muni["Nombre"])
        if img:
            st.image(img, width='stretch')

    with col2:
        # Name and button side by side
        name_col, btn_col = st.columns([5, 1])
        with name_col:
            st.markdown(f"<div class='municipality-name'>{muni['Nombre']}</div>", unsafe_allow_html=True)
        with btn_col:
            if st.button("Ver detalles", key=f"details_btn_{row_idx}_{muni['codigo']}"):
                st.session_state["selected_municipality_code"] = muni["codigo"]
                st.session_state["details_origin"] = "list"
                st.session_state["suppress_map_selection"] = True
                st.session_state["switch_view_to"] = ":material/list: Lista de municipios"
                st.rerun()
        
        # Calculate color based on score (gradient from red to green)
        score = muni["weighted_score"]
        if score >= 70:
            bg_color = "#A8D5BA"  # Pastel green
        elif score >= 50:
            bg_color = "#F9E79F"  # Pastel yellow
        else:
            bg_color = "#F5B7B1"  # Pastel red
        
        st.markdown(
            f'<div class="score-badge" style="background-color: {bg_color}; color: #333;">Puntuación: {score:.1f}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f":material/group: **Población:** {int(muni['IDE_PoblacionTotal']):,}<br>"
                f":material/payments: **Precio vivienda:** {muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²<br>"
                f":material/schedule: **Horas a la semana en transporte:** {muni['AccessibilityHoursWeekly']:.1f}"
            ),
            unsafe_allow_html=True,
        )

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
    st.markdown("Explora los municipios de la Comunidad de Madrid ordenados según tu perfil. La **puntuación** refleja qué tan bien se ajusta cada municipio a tus preferencias y prioridades.")
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

    for idx, row in page_df.iterrows():
        # Show details inline if this municipality is selected
        if ("selected_municipality_code" in st.session_state and 
            st.session_state.get("details_origin") == "list" and
            st.session_state["selected_municipality_code"] == row["codigo"]):
            st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)
            from ui.details_view import render_details
            # Look up fresh data from current scores_df
            selected_muni = scores_df[scores_df["codigo"] == st.session_state["selected_municipality_code"]]
            if len(selected_muni) > 0:
                render_details(selected_muni.iloc[0], images, scores_df)
            st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)
        else:
            render_municipality_card(row, images, idx)


    # Bottom pagination
    st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)

    _render_pagination(current_page, num_pages, "bottom")
