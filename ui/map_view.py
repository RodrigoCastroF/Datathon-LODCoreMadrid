# ui/map_view.py
"""Map visualization component."""

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st


def create_heatmap(gdf: gpd.GeoDataFrame):
    """Create choropleth map of municipalities.
    
    Args:
        gdf: GeoDataFrame with weighted_score column
        
    Returns:
        Plotly figure
    """
    gdf_plot = gdf.to_crs(epsg=4326)

    fig = px.choropleth_mapbox(
        gdf_plot,
        geojson=gdf_plot.geometry.__geo_interface__,
        locations=gdf_plot.index,
        color="weighted_score",
        color_continuous_scale=["#DFD1B6", "#6FB5BA", "#568EE2", "#3D517B"],
        range_color=[gdf_plot["weighted_score"].min(), gdf_plot["weighted_score"].max()],
        mapbox_style="open-street-map",
        zoom=8,
        center={"lat": 40.4168, "lon": -3.7038},
        opacity=0.7,
        title="Mapa de municipios según tu perfil",
        custom_data=[gdf_plot["Nombre"]],
        labels={"weighted_score": "Puntuación (más alto = mejor)"},
    )

    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>Puntuación: %{z:.1f}<extra></extra>"
    )
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        clickmode="event+select",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# New function:
def render_map_view(gdf: gpd.GeoDataFrame, scores_df: pd.DataFrame) -> None:
    """Render map view with click handling.
    
    Args:
        gdf: GeoDataFrame with municipality boundaries and scores
        scores_df: DataFrame with municipality scores
    """
    if len(gdf) == 0:
        st.warning("No hay municipios disponibles para mostrar.")
        return

    # Check if in comparison mode
    in_comparison_mode = st.session_state.get("view_selector") == ":material/balance: Comparación"
    
    if in_comparison_mode:
        st.markdown(":material/prompt_suggestion: **Consejo:** haz clic en un municipio del mapa para añadirlo a la comparación.     :material/arrow_drop_down_circle:")
    else:
        st.markdown(":material/prompt_suggestion: **Consejo:** haz clic en un municipio del mapa para ver más detalles abajo.     :material/arrow_drop_down_circle:")
    
    suppress = st.session_state.pop("suppress_map_selection", False)

    fig = create_heatmap(gdf)
    event = st.plotly_chart(
        fig,
        key="heatmap",
        width='stretch',
        on_select="rerun",
        selection_mode="points",
    )

    if not suppress and event and event.selection and event.selection["point_indices"]:
        idx = event.selection["point_indices"][0]
        clicked_name = gdf.iloc[idx]["Nombre"]
        selected_row = scores_df[scores_df["Nombre"] == clicked_name].iloc[0]

        if in_comparison_mode:
            # Add to comparison list
            if "comparison_municipalities" not in st.session_state:
                st.session_state["comparison_municipalities"] = []
            
            comparison_list = st.session_state["comparison_municipalities"]
            
            if selected_row["codigo"] not in comparison_list and len(comparison_list) < 4:
                comparison_list.append(selected_row["codigo"])
                st.session_state["comparison_municipalities"] = comparison_list
                st.rerun()
            elif selected_row["codigo"] in comparison_list:
                st.info(f"✓ {clicked_name} ya está en la comparación")
            else:
                st.warning(":material/warning: Máximo 4 municipios en comparación. Elimina uno para añadir otro.")
        else:
            # Show details inline - store only the code
            st.session_state["selected_municipality_code"] = selected_row["codigo"]
            st.session_state["details_origin"] = "map"
    
    # Show details inline in map view
    if "selected_municipality_code" in st.session_state and st.session_state.get("details_origin") == "map":
        st.markdown("---")
        from ui.details_view import render_details
        from core.data_loader import load_placeholder_images
        
        # Look up fresh data from current scores_df
        selected_muni = scores_df[scores_df["codigo"] == st.session_state["selected_municipality_code"]]
        if len(selected_muni) > 0:
            images = load_placeholder_images()
            render_details(selected_muni.iloc[0], images, scores_df)
        else:
            # Municipality no longer in filtered results
            st.session_state.pop("selected_municipality_code", None)
            st.session_state.pop("details_origin", None)


