# ui/details_view.py - Complete updated file

# ui/details_view.py
"""Municipality details and comparison panel."""

import random
from typing import Dict, Optional

import pandas as pd
import streamlit as st
from PIL import Image

from config.constants import CRITERIA, CRITERIA_ICONS, CRITERIA_LABELS, BENEFIT_COLUMNS, COST_COLUMNS


def show_single_municipality_details(
    muni: pd.Series,
    images: Dict[str, Optional[Image.Image]],
    title: Optional[str] = None,
    all_scores: Optional[pd.DataFrame] = None,
) -> None:
    """Show details for one municipality.
    
    Args:
        muni: Municipality data series
        images: Dictionary of placeholder images
        title: Optional section title
        all_scores: Full scores DataFrame for ranking calculation
    """
    if title:
        st.markdown(f"**{title}**")

    col1, col2 = st.columns([1, 2])

    with col1:
        from core.data_loader import get_municipality_image

        img = get_municipality_image(muni["Nombre"])
        if img:
            st.image(img)

    with col2:
        st.markdown(
            f'<div class="score-badge">Puntuación: {muni["weighted_score"]:.1f}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f":material/group: | **Población:** {int(muni['IDE_PoblacionTotal']):,}")
        st.markdown(f":material/payments: | **Precio vivienda:** {muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²")
        st.markdown(f":material/schedule: | **Horas a la semana en transporte:** {muni['AccessibilityHoursWeekly']:.1f}")

    # Legend
    st.markdown("#### **Desglose por criterio**")
    st.markdown(
        '<div style="font-size: 12px; color: #666; margin-bottom: 1rem;">'
        '<span style="color: #377F86;">●</span> Excelente (≥70%) | '
        '<span style="color: #C35309;">●</span> Promedio (40-69%) | '
        '<span style="color: #C33241;">●</span> Bajo (<40%)'
        '</div>',
        unsafe_allow_html=True
    )

    for crit in CRITERIA:
        norm_col = f"NORM_{crit}"
        contrib_col = f"CONTRIB_{crit}"
        if norm_col not in muni or contrib_col not in muni:
            continue

        from config.constants import CRITERIA_TOOLTIPS
        
        icon = CRITERIA_ICONS[crit]
        label = CRITERIA_LABELS[crit]
        tooltip = CRITERIA_TOOLTIPS.get(crit, "")
        value = float(muni[norm_col])
        contrib = float(muni[contrib_col])
        
        # Get raw value and format
        if crit == "AccessibilityHoursWeekly":
            raw_value = f"{muni['AccessibilityHoursWeekly']:.1f} h/semana"
        elif crit == "HousePriceSqm":
            raw_value = f"{muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²"
        elif crit in BENEFIT_COLUMNS:
            raw_col = BENEFIT_COLUMNS[crit]
            raw_value = f"{muni[raw_col]:.2f}"
        else:
            raw_value = ""
        
        # Calculate rank
        rank = None
        total_munis = None
        if all_scores is not None:
            sorted_scores = all_scores.sort_values(norm_col, ascending=False).reset_index(drop=True)
            rank = sorted_scores[sorted_scores['codigo'] == muni['codigo']].index[0] + 1
            total_munis = len(sorted_scores)

        col_label, col_bar = st.columns([2, 3])
        with col_label:
            st.markdown(f"{icon} | **{label}**")
        with col_bar:
            pct = int(value * 100)
            color = "#377F86" if pct >= 70 else "#C35309" if pct >= 40 else "#C33241"
            
            # Build rank text
            rank_text = f" | Puesto {rank}/{total_munis}" if rank and total_munis else ""
            
            st.markdown(
                f'<div style="background-color: #e9ecef; border-radius: 10px; height: 20px; width: 100%;">'
                f'<div style="background-color: {color}; height: 20px; width: {pct}%; border-radius: 10px; '
                f'display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">{pct}%</div></div>'
                f'<div style="font-size: 11px; color: #555;">'
                f'{raw_value}{rank_text} '
                f'<span title="{tooltip}" style="cursor: help; color: #888; margin-left: 8px;">ⓘ</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_details(municipality: pd.Series, images: Dict, all_scores: pd.DataFrame) -> None:
    """Render municipality details panel with optional comparison.
    
    Args:
        municipality: Selected municipality data
        images: Dictionary of placeholder images
        all_scores: Full scores DataFrame for comparison
    """
    with st.container():
        header_col1, header_col2 = st.columns([14, 1])
        with header_col1:
            st.markdown("## :material/location_on: Detalles del municipio")
            st.markdown(f"### **{municipality['Nombre']}**")
        with header_col2:
            st.markdown("""
                <style>
                div[data-testid="column"]:last-child > div > div > div > div.stButton {
                    display: flex;
                    justify-content: flex-end;
                }
                </style>
            """, unsafe_allow_html=True)
            if st.button("✕", key=f"close_details_{municipality['codigo']}", help="Cerrar"):
                origin = st.session_state.get("details_origin")
                if origin == "map":
                    st.session_state["switch_view_to"] = ":material/map: Mapa de municipios"
                elif origin == "list":
                    st.session_state["switch_view_to"] = ":material/list: Lista de municipios"
                st.session_state["suppress_map_selection"] = True
                for key in ["selected_municipality", "comparison_municipality", "comparison_selector",
                           "comparison_selector_in_panel", "details_origin"]:
                    st.session_state.pop(key, None)
                st.rerun()


        comparison_mode = "comparison_municipality" in st.session_state

        if comparison_mode:
            comparison_muni = st.session_state.comparison_municipality
            col1, col2, col3 = st.columns([5, 1, 5])
            
            with col1:
                show_single_municipality_details(municipality, images, ":material/home: Municipio principal", all_scores)
            with col2:
                st.markdown("<br><br><br>**VS**", unsafe_allow_html=True)
            with col3:
                comp_header_col1, comp_header_col2 = st.columns([3, 1])
                with comp_header_col1:
                    st.markdown("**:material/search: Comparación**")
                with comp_header_col2:
                    if st.button("↻", key=f"end_comparison_{municipality['codigo']}", help="Terminar comparación"):
                        st.session_state["clear_comparison_only"] = True
                        st.rerun()

                show_single_municipality_details(comparison_muni, images, None, all_scores)

                st.markdown("---\n**Cambiar municipio:**")
                options = [f"{row['Nombre']} (Puntuación: {row['weighted_score']:.1f})"
                          for _, row in all_scores.iterrows() if row["codigo"] != municipality["codigo"]]

                if options:
                    current_selection = f"{comparison_muni['Nombre']} (Puntuación: {comparison_muni['weighted_score']:.1f})"
                    try:
                        current_index = options.index(current_selection) + 1
                    except ValueError:
                        current_index = 0

                    selected = st.selectbox("Selecciona otro municipio:", ["Selecciona un municipio..."] + options,
                                          index=current_index, key="comparison_selector_in_panel")

                    if selected != "Selecciona un municipio..." and selected != current_selection:
                        comp_name = selected.split(" (Puntuación:")[0]
                        comp_row = all_scores[all_scores["Nombre"] == comp_name].iloc[0]
                        st.session_state["comparison_municipality"] = comp_row
                        st.rerun()
        else:
            show_single_municipality_details(municipality, images, all_scores=all_scores)
            st.markdown("---")
            st.subheader(":material/search: Comparar con otro municipio")
            options = [f"{row['Nombre']} (Puntuación: {row['weighted_score']:.1f})"
                      for _, row in all_scores.iterrows() if row["codigo"] != municipality["codigo"]]
            if options:
                selected = st.selectbox("Selecciona municipio para comparar:", ["Selecciona un municipio..."] + options,
                                      key="comparison_selector")
                if selected != "Selecciona un municipio...":
                    comp_name = selected.split(" (Puntuación:")[0]
                    comp_row = all_scores[all_scores["Nombre"] == comp_name].iloc[0]
                    st.session_state["comparison_municipality"] = comp_row
                    st.rerun()
