# ui/comparison_view.py
"""Multi-municipality comparison view with radar chart."""

from typing import Dict, Optional, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from config.constants import CRITERIA, CRITERIA_LABELS, CRITERIA_ICONS


def render_municipality_comparison_card(muni: pd.Series, images: Dict[str, Optional[Image.Image]], index: int) -> None:
    """Render single municipality card in comparison view.
    
    Args:
        muni: Municipality data series
        images: Dictionary of placeholder images
        index: Position index for unique keys
    """
    st.markdown('<div class="municipality-card">', unsafe_allow_html=True)
    
    # Remove button in top-right
    col_content, col_remove = st.columns([5, 1])
    with col_remove:
        st.markdown("""
            <style>
            div[data-testid="column"] > div > div > div > div.stButton {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)
        if st.button("✕", key=f"remove_comparison_{index}_{muni['codigo']}", help="Quitar de comparación"):
            comparison_list = st.session_state.get("comparison_municipalities", [])
            if muni["codigo"] in comparison_list:
                comparison_list.remove(muni["codigo"])
                st.session_state["comparison_municipalities"] = comparison_list
                st.rerun()
    
    with col_content:
        # Image
        from core.data_loader import get_municipality_image
        img = get_municipality_image(muni["Nombre"])
        if img:
            st.image(img, width='stretch')
        
        # Name and score
        st.markdown(f"<div class='municipality-name'>{muni['Nombre']}</div>", unsafe_allow_html=True)
        st.markdown(
            f'<div class="score-badge">Puntuación: {muni["weighted_score"]:.1f}</div>',
            unsafe_allow_html=True,
        )
        
        # Key metrics
        st.markdown(f":material/group: **Población:** {int(muni['IDE_PoblacionTotal']):,}")
        st.markdown(f":material/payments: **Precio:** {muni['IDE_PrecioPorMetroCuadrado']:.0f} €/m²")
        st.markdown(f":material/schedule: **Transporte:** {muni['AccessibilityHoursMonthly']:.1f} h/mes")
    
    st.markdown("</div>", unsafe_allow_html=True)


def create_radar_chart(municipalities: List[pd.Series]) -> go.Figure:
    """Create interactive radar chart comparing municipalities across all criteria.
    
    Args:
        municipalities: List of municipality data series
        
    Returns:
        Plotly figure with radar chart
    """
    colors = ["#568EE2", "#6FB5BA", "#C35309", "#A59FD0"]
    
    fig = go.Figure()
    
    for idx, muni in enumerate(municipalities):
        # Get normalized values for all criteria (0-100 scale)
        values = [float(muni[f"NORM_{crit}"]) * 100 for crit in CRITERIA]
        values.append(values[0])  # Close the polygon
        
        # Get criterion labels
        labels = [CRITERIA_LABELS[crit] for crit in CRITERIA]
        labels.append(labels[0])  # Close the polygon
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name=muni["Nombre"],
            line=dict(color=colors[idx % len(colors)], width=2),
            fillcolor=colors[idx % len(colors)],
            opacity=0.6,
            hovertemplate="<b>%{fullData.name}</b><br>%{theta}: %{r:.1f}%<extra></extra>",
            hoverlabel=dict(
                bgcolor=colors[idx % len(colors)],
                font_size=14,
                font_color="white"
            )
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix="%",
                tickfont=dict(size=11),
                gridcolor="rgba(128, 128, 128, 0.2)"
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                rotation=90
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=13),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(128,128,128,0.3)",
            borderwidth=1
        ),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=100, r=100, t=50, b=120),
        hovermode='closest'
    )
    
    return fig


def render_comparison_view(scores_df: pd.DataFrame, images: Dict[str, Optional[Image.Image]]) -> None:
    """Render multi-municipality comparison view.
    
    Args:
        scores_df: DataFrame with municipality scores
        images: Dictionary of placeholder images
    """
    if "comparison_municipalities" not in st.session_state:
        st.session_state["comparison_municipalities"] = []
    
    comparison_codes = st.session_state["comparison_municipalities"]
    
    st.markdown("### :material/balance: Comparación de municipios")
    st.markdown("Compara hasta 4 municipios lado a lado y visualiza sus fortalezas en el gráfico radar.")
    
    # Get municipality data
    comparison_munis = []
    for code in comparison_codes:
        muni_data = scores_df[scores_df["codigo"] == code]
        if len(muni_data) > 0:
            comparison_munis.append(muni_data.iloc[0])
    
    # Municipality cards
    num_munis = len(comparison_munis)
    
    if num_munis == 0:
        st.info(":material/touch_app: Selecciona municipios para comenzar la comparación (usa el buscador abajo o haz clic en el mapa)")
    
    # Dynamic columns
    if num_munis < 4:
        cols = st.columns(num_munis + 1)
    else:
        cols = st.columns(4)
    
    # Render municipality cards
    for idx, muni in enumerate(comparison_munis):
        with cols[idx]:
            render_municipality_comparison_card(muni, images, idx)
    
    # Add municipality button
    if num_munis < 4:
        with cols[num_munis]:
            st.markdown("### :material/add_circle: Añadir municipio")
            
            # Searchable selectbox
            available_munis = scores_df[~scores_df["codigo"].isin(comparison_codes)]
            options = [f"{row['Nombre']} (Puntuación: {row['weighted_score']:.1f})" 
                      for _, row in available_munis.iterrows()]
            
            if options:
                selected = st.selectbox(
                    "Buscar municipio:",
                    ["Selecciona un municipio..."] + options,
                    key=f"add_comparison_{num_munis}"
                )
                
                if selected != "Selecciona un municipio...":
                    muni_name = selected.split(" (Puntuación:")[0]
                    muni_code = available_munis[available_munis["Nombre"] == muni_name].iloc[0]["codigo"]
                    comparison_codes.append(muni_code)
                    st.session_state["comparison_municipalities"] = comparison_codes
                    st.rerun()
    
    # Radar chart
    if num_munis > 0:
        st.markdown("---")
        st.markdown("### :material/analytics: Comparación visual por criterios")
        st.caption(":material/info: Pasa el ratón sobre el gráfico para ver valores detallados. Haz clic en la leyenda para resaltar un municipio.")
        
        fig = create_radar_chart(comparison_munis)
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
