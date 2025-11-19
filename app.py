# app.py
"""LodCORE Madrid - Municipality Finder
Main Streamlit application for ranking municipalities by accessibility and quality of life.
"""

import numpy as np
import streamlit as st

from config.styles import apply_styles
from config.constants import CRITERIA, BENEFIT_COLUMNS, COST_COLUMNS
from core.data_loader import load_data, load_placeholder_images
from core.accessibility import compute_accessibility_hours
from core.ahp import preferences_to_weights
from core.scoring import normalize_criteria, compute_scores, equal_weights
from ui.questionnaire import render_questionnaire
from ui.map_view import render_map_view
from ui.list_view import render_list_view
from ui.details_view import render_details
from ui.comparison_view import render_comparison_view
from ui.sensitivity import render_sensitivity


def main() -> None:
    """Main application entry point."""
    # Apply styles and page config
    apply_styles()
    
    # Handle view switching state
    if "view_selector" not in st.session_state:
        st.session_state["view_selector"] = ":material/map: Mapa de municipios"
    
    if st.session_state.get("switch_view_to"):
        st.session_state["view_selector"] = st.session_state["switch_view_to"]
        st.session_state["switch_view_to"] = None
    
    if st.session_state.get("clear_comparison_only"):
        for key in ["comparison_municipality", "comparison_selector_in_panel", "clear_comparison_only"]:
            st.session_state.pop(key, None)
    
    # Clear selected municipality when switching views
    if "previous_view" not in st.session_state:
        st.session_state["previous_view"] = ":material/map: Mapa de municipios"

    # Header
    st.markdown('<h1 class="main-header">🏘️ Living on the Edge</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="tagline">Encuentra tu municipio ideal en la Comunidad de Madrid según tu estilo de vida, tu familia y tus prioridades.</p>',
        unsafe_allow_html=True,
    )

    # Add anchor for back-to-top
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)

    # Load data
    df_raw, gdf_raw = load_data()
    images = load_placeholder_images()
    
    # Render questionnaire and get user preferences
    prefs = render_questionnaire(df_raw)
    
    # Filter by population
    df = df_raw.copy()
    if "IDE_PoblacionTotal" in df.columns:
        df = df[(df["IDE_PoblacionTotal"] >= prefs["pop_min"]) & 
                (df["IDE_PoblacionTotal"] <= prefs["pop_max"])].copy()
    
    # Compute accessibility
    acc_df = compute_accessibility_hours(
        df=df,
        freq_car=prefs["w_car"],
        freq_sport=prefs["w_sport"],
        freq_hospital=prefs["w_hospital"],
        edu_has_kids=prefs["edu_has_kids"],
        edu_variant=prefs["edu_variant"],
        edu_levels=prefs["edu_levels"],
    )
    
    df_scored = df.merge(acc_df[["codigo", "AccessibilityHoursWeekly"]], on="codigo", how="left")
    
    # Normalize criteria
    norm_df = normalize_criteria(df_scored, BENEFIT_COLUMNS, COST_COLUMNS)
    
    # Compute weights via AHP
    try:
        # Invert ranks: higher user value → lower AHP rank (higher priority)
        # Keep 0 as 0 to indicate "no importance"
        inverted_ranks = [11 - r if r > 0 else 0 for r in prefs["ranks"]]
        w_vec = preferences_to_weights(np.array(inverted_ranks, dtype=float), mode="ranking")
        weights = {CRITERIA[i]: float(w_vec[i]) for i in range(len(CRITERIA))}
    except Exception as e:
        st.sidebar.error(f":material/error: Error: {e}")
        st.sidebar.info("Usando pesos iguales como respaldo.")
        weights = equal_weights(CRITERIA)
    
    # Compute scores
    with st.spinner("Calculando puntuaciones de municipios..."):
        scores_df = compute_scores(norm_df, weights)
    
    # Prepare map data
    with st.spinner("Preparando mapa..."):
        gdf = gdf_raw.merge(
            scores_df[["codigo", "Nombre", "Score", "weighted_score", "AccessibilityHoursWeekly",
                      "IDE_PoblacionTotal", "IDE_PrecioPorMetroCuadrado"] +
                     [c for c in scores_df.columns if c.startswith("NORM_") or c.startswith("CONTRIB_")]],
            on=["Nombre"],
            how="inner",
        )
    
    # Main view selector
    view_option = st.radio(
        "Selecciona vista:",
        [":material/map: Mapa de municipios", 
         ":material/list: Lista de municipios", 
         ":material/balance: Comparación"],
        horizontal=True,
        key="view_selector",
    )

    # Clear selected municipality when view changes
    if st.session_state["previous_view"] != view_option:
        st.session_state.pop("selected_municipality", None)
        st.session_state.pop("details_origin", None)
        st.session_state["previous_view"] = view_option    

    # CSV download
    st.download_button(
        label="📥 Descargar resultados (CSV)",
        data=scores_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="lodcore_municipios.csv",
        mime="text/csv",
        help="Descarga todos los municipios con sus puntuaciones y detalles"
    )
    
    # Render selected view
    if view_option == ":material/map: Mapa de municipios":
        render_map_view(gdf, scores_df)
    elif view_option == ":material/list: Lista de municipios":
        render_list_view(scores_df, images)
    else:
        render_comparison_view(scores_df, images)
    

    # Sensitivity analysis
    st.markdown('<hr style="margin: -0.25rem 0; border: none; border-top: 1px solid #ddd;">', unsafe_allow_html=True)
    render_sensitivity(scores_df, weights, norm_df, compute_scores)

    # Back to top button
    st.markdown(
        '<a href="#top" class="back-to-top" title="Volver arriba">:material/keyboard_arrow_up:</a>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
