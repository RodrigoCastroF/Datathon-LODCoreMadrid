import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
from PIL import Image
import json
import os

# Page configuration
st.set_page_config(
    page_title="Living on the Edge",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1f77b4, #17a2b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .municipality-card {
        background: linear-gradient(145deg, #ffffff, #f0f2f5);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
        transition: transform 0.2s ease-in-out;
    }
    
    .municipality-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    .score-badge {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        font-size: 0.9rem;
    }
    
    .municipality-name {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.8rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .detail-panel {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .concept-icon {
        font-size: 1.3rem;
        margin-right: 0.5rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    .metric-container {
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    
    .comparison-header {
        background: linear-gradient(45deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load municipality data and geographic boundaries"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load municipality data
        csv_path = os.path.join(script_dir, 'municipalities.csv')
        if not os.path.exists(csv_path):
            st.error(f"No se encuentra el archivo municipalities.csv en {csv_path}")
            st.stop()
        df = pd.read_csv(csv_path)
        
        # Load geographic data
        shp_path = os.path.join(script_dir, 'boundaries', 'recintos_municipales_inspire_peninbal_etrs89.shp')
        if not os.path.exists(shp_path):
            st.error(f"No se encuentra el archivo SHP en {shp_path}")
            st.stop()
        
        # Suppress GDAL warnings temporarily
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gdf = gpd.read_file(shp_path)
        
        madrid_gdf = gdf[gdf['CODNUT2'] == 'ES30'].copy()
        
        if len(madrid_gdf) == 0:
            st.error("No se encontraron municipios de Madrid en los datos geográficos")
            st.stop()
        
        # Ensure NATCODE columns have the same type for merging
        # Convert both to string to avoid type mismatch
        madrid_gdf['NATCODE'] = madrid_gdf['NATCODE'].astype(str)
        df['NATCODE'] = df['NATCODE'].astype(str)
        
        
        # Merge geographic data with municipality data
        merged_gdf = madrid_gdf.merge(df, on=['NAMEUNIT', 'NATCODE'], how='inner')
        
        if len(merged_gdf) == 0:
            st.error("No se pudieron combinar los datos geográficos con los datos de municipios")
            st.write("Municipios en CSV:", df['NAMEUNIT'].head(10).tolist())
            st.write("Municipios en SHP:", madrid_gdf['NAMEUNIT'].head(10).tolist())
            st.stop()
        
        return df, merged_gdf
        
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        st.stop()

@st.cache_data
def load_placeholder_images():
    """Load placeholder images"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    images = {}
    for i in range(1, 7):
        try:
            img_path = os.path.join(script_dir, 'photos', f'placeholder{i}.jpeg')
            img = Image.open(img_path)
            images[f'placeholder{i}'] = img
        except:
            images[f'placeholder{i}'] = None
    return images

def calculate_weighted_score(row, weights, filters):
    """Calculate weighted score for a municipality based on user preferences"""
    concepts = ['schools', 'pharmacies', 'hospitals', 'parks', 'cinemas', 'restaurants', 'supermarkets']
    
    # Check filters first
    for concept in concepts:
        if filters[concept] and row[concept] < 70:  # Required concepts need high accessibility
            return 0  # Municipality doesn't meet requirements
    
    # Calculate weighted score
    score = 0
    total_weight = 0
    
    for concept in concepts:
        weight = weights[concept]
        score += row[concept] * weight
        total_weight += weight
    
    if total_weight > 0:
        normalized_score = score / total_weight
    else:
        normalized_score = np.mean([row[concept] for concept in concepts])
    
    return round(normalized_score, 1)

def filter_by_criteria(df, population_range, rent_range, temp_range):
    """Filter municipalities by additional criteria"""
    filtered_df = df[
        (df['population'] >= population_range[0]) & 
        (df['population'] <= population_range[1]) &
        (df['rent'] >= rent_range[0]) & 
        (df['rent'] <= rent_range[1]) &
        (df['maxtemp'] >= temp_range[0]) & 
        (df['maxtemp'] <= temp_range[1])
    ].copy()
    
    return filtered_df

def get_concept_icon(concept):
    """Get icon for each concept"""
    icons = {
        'schools': '🏫',
        'pharmacies': '💊',
        'hospitals': '🏥',
        'parks': '🌳',
        'cinemas': '🎬',
        'restaurants': '🍽️',
        'supermarkets': '🛒'
    }
    return icons.get(concept, '📍')

def create_heatmap(gdf):
    """Create interactive heatmap"""
    # Convert to WGS84 for plotting
    gdf_plot = gdf.to_crs(epsg=4326)
    
    # Create color scale based on weighted score
    fig = px.choropleth_mapbox(
        gdf_plot,
        geojson=gdf_plot.geometry.__geo_interface__,
        locations=gdf_plot.index,
        color='weighted_score',
        color_continuous_scale='RdYlBu_r',
        range_color=[gdf_plot['weighted_score'].min(), gdf_plot['weighted_score'].max()],
        mapbox_style="open-street-map",
        zoom=8,
        center={"lat": 40.4168, "lon": -3.7038},  # Madrid center
        opacity=0.7,
        title="Mapa de accesibilidad de municipios. Haz clic en un municipio para ver más detalles",
        custom_data=[gdf_plot['NAMEUNIT'], gdf_plot['population'], gdf_plot['rent'], gdf_plot['maxtemp']],
        labels={'weighted_score': 'Puntuación'}
    )
    
    # Update hover template with correct data access
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>' +
                     'Puntuación: %{z:.1f}<br>' +
                     'Población: %{customdata[1]:,}<br>' +
                     'Alquiler: %{customdata[2]:.0f}€/mes<br>' +
                     'Temp. máx: %{customdata[3]:.0f}°C<br>' +
                     '<i>Haz clic para ver detalles</i><extra></extra>'
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    return fig

def main():
    # Check if we need to clear municipality selection
    if st.session_state.get('clear_municipality_selection', False):
        # Clear all municipality selections and related state
        keys_to_remove = [
            'selected_municipality',
            'comparison_municipality',
            'comparison_selector',
            'comparison_selector_in_panel',
            'map_municipality_selector',
            'clear_municipality_selection'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    # Check if we need to clear only comparison
    if st.session_state.get('clear_comparison_only', False):
        # Clear only comparison state
        keys_to_remove = [
            'comparison_municipality',
            'comparison_selector_in_panel',
            'clear_comparison_only'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    # Header
    st.markdown('<h1 class="main-header">🏘️ Living on the Edge</h1>', unsafe_allow_html=True)
    st.markdown("*Encuentra el municipio perfecto de la Comunidad de Madrid según tus necesidades de accesibilidad*")
    
    # Demo notice
    st.warning("⚠️ **DEMO**: Esta es una aplicación de demostración. Todos los datos mostrados son aleatorios y no reflejan información real de los municipios.")
    
    # Load data
    df, gdf = load_data()
    images = load_placeholder_images()
    
    # Sidebar for user preferences
    st.sidebar.header("Preferencias")
    
    # Concept importance sliders
    st.sidebar.subheader("Importancia")
    weights = {}
    concepts = ['schools', 'pharmacies', 'hospitals', 'parks', 'cinemas', 'restaurants', 'supermarkets']
    concept_names = {
        'schools': 'Colegios',
        'pharmacies': 'Farmacias', 
        'hospitals': 'Hospitales',
        'parks': 'Parques',
        'cinemas': 'Cines',
        'restaurants': 'Restaurantes',
        'supermarkets': 'Supermercados'
    }
    
    for concept in concepts:
        weights[concept] = st.sidebar.slider(
            f"{get_concept_icon(concept)} {concept_names[concept]}",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help=f"Importancia de la accesibilidad a {concept_names[concept].lower()}"
        )
    
    # Requirement filters
    st.sidebar.subheader("Requisitos obligatorios")
    filters = {}
    for concept in concepts:
        filters[concept] = st.sidebar.checkbox(
            f"Requiere {concept_names[concept].lower()}",
            value=False,
            help=f"El municipio debe tener buena accesibilidad a {concept_names[concept].lower()}"
        )
    
    # Additional criteria
    st.sidebar.subheader("Criterios adicionales")
    
    population_range = st.sidebar.slider(
        "👥 Rango de Población",
        min_value=int(df['population'].min()),
        max_value=int(df['population'].max()),
        value=(int(df['population'].min()), int(df['population'].max())),
        step=1000,
        format="%d"
    )
    st.sidebar.write(f"Rango seleccionado: {population_range[0]:,} - {population_range[1]:,}")
    
    rent_range = st.sidebar.slider(
        "💰 Rango de Alquiler (€/mes)",
        min_value=int(df['rent'].min()),
        max_value=int(df['rent'].max()),
        value=(int(df['rent'].min()), int(df['rent'].max())),
        step=50
    )
    
    temp_range = st.sidebar.slider(
        "🌡️ Temperatura Máxima (°C)",
        min_value=int(df['maxtemp'].min()),
        max_value=int(df['maxtemp'].max()),
        value=(int(df['maxtemp'].min()), int(df['maxtemp'].max())),
        step=1
    )
    
    # Filter data based on criteria
    filtered_df = filter_by_criteria(df, population_range, rent_range, temp_range)
    
    # Calculate weighted scores
    filtered_df['weighted_score'] = filtered_df.apply(
        lambda row: calculate_weighted_score(row, weights, filters), axis=1
    )
    
    # Remove municipalities with score 0 (don't meet requirements)
    filtered_df = filtered_df[filtered_df['weighted_score'] > 0]
    
    # Sort by score
    filtered_df = filtered_df.sort_values('weighted_score', ascending=False).reset_index(drop=True)
    
    # Update geographic data
    filtered_gdf = gdf[gdf['NAMEUNIT'].isin(filtered_df['NAMEUNIT'])].copy()
    filtered_gdf = filtered_gdf.merge(
        filtered_df[['NAMEUNIT', 'weighted_score']], 
        on='NAMEUNIT', 
        how='inner'
    )
    
    # Main panel view selection
    view_option = st.radio(
        "Selecciona vista:",
        ["🗺️ Mapa de calor", "📋 Vista de lista"],
        horizontal=True
    )
    
    if view_option == "🗺️ Mapa de calor":
        if len(filtered_gdf) > 0:
            fig = create_heatmap(filtered_gdf)
            clicked_data = st.plotly_chart(fig, width="stretch", key="heatmap", on_select="rerun")
            
            # Handle click on map
            if clicked_data and clicked_data.selection and clicked_data.selection.get('points'):
                try:
                    point_data = clicked_data.selection['points'][0]
                    if 'customdata' in point_data and len(point_data['customdata']) > 0:
                        municipality_name = point_data['customdata'][0]
                        selected_municipality_data = filtered_df[
                            filtered_df['NAMEUNIT'] == municipality_name
                        ].iloc[0]
                        st.session_state.selected_municipality = selected_municipality_data
                        st.rerun()
                except:
                    pass  # Silently ignore click errors
            
        else:
            st.warning("No hay municipios que cumplan con los criterios seleccionados.")
    
    else:  # List view
        st.subheader("📋 Lista de municipios ordenados por puntuación")
        
        if len(filtered_df) > 0:
            # Display results count and show only top 6
            total_count = len(filtered_df)
            display_df = filtered_df.head(6)
            
            if total_count > 6:
                st.info(f"Mostrando los top 6 municipios de {total_count} que cumplen tus criterios")
            else:
                st.info(f"Se encontraron {total_count} municipios que cumplen tus criterios")
            
            # Create compact municipality cards in single lines
            for idx, row in display_df.iterrows():
                # Create single-line layout with all information
                col_img, col_name, col_pop, col_rent, col_temp, col_score = st.columns([1, 2.5, 1.5, 1.5, 1.5, 1])
                
                with col_img:
                    # Consistent placeholder image per municipality
                    random.seed(hash(row['NAMEUNIT']))
                    img_key = f"placeholder{random.randint(1, 6)}"
                    if images[img_key] is not None:
                        st.image(images[img_key], width=60)
                
                with col_name:
                    # Create clickable municipality name
                    municipality_name = row["NAMEUNIT"]
                    button_key = f"name_{row['NAMEUNIT']}_{row['weighted_score']}"
                    if st.button(municipality_name, key=button_key, 
                                help="Haz clic para ver detalles",
                                type="secondary"):
                        st.session_state.selected_municipality = row
                        st.rerun()
                
                with col_pop:
                    st.write(f"👥 {row['population']:,}")
                    
                with col_rent:
                    st.write(f"💰 {row['rent']}€")
                    
                with col_temp:
                    st.write(f"🌡️ {row['maxtemp']}°C")
                    
                with col_score:
                    st.markdown(f'<div class="score-badge">{row["weighted_score"]}</div>', unsafe_allow_html=True)
                
                # Add thin separator line
                st.markdown('<hr style="margin: 0.5rem 0; border: 0; height: 1px; background: #ddd;">', unsafe_allow_html=True)
        else:
            st.warning("No hay municipios que cumplan con los criterios seleccionados.")
    
    # Show municipality details if selected
    if 'selected_municipality' in st.session_state:
        # Add clear separator
        st.markdown("---")
        
        st.markdown("### 📍 Detalles del municipio")
        
        show_municipality_details(st.session_state.selected_municipality, images, concept_names, filtered_df, weights, filters)

def show_municipality_details(municipality, images, concept_names, all_municipalities, weights, filters):
    """Show detailed information about a selected municipality"""
    
    # Recalculate weighted score with current preferences
    current_score = calculate_weighted_score(municipality, weights, filters)
    municipality = municipality.copy()
    municipality['weighted_score'] = current_score
    
    # Create container for proper layout
    with st.container():
        # Header with close button
        header_col1, header_col2 = st.columns([4, 1])
        with header_col1:
            st.markdown(f"**{municipality['NAMEUNIT']}**")
        with header_col2:
            # Create unique key based on municipality name to avoid conflicts
            close_key = f"close_details_{municipality['NAMEUNIT']}"
            if st.button("❌ Cerrar", key=close_key):
                # Clear all municipality selections and related state immediately
                st.session_state.clear_municipality_selection = True
                st.rerun()
        
        # Check if we're in comparison mode
        comparison_mode = 'comparison_municipality' in st.session_state
        
        if comparison_mode:
            # Show both municipalities side by side
            comparison_municipality = st.session_state.comparison_municipality.copy()
            comparison_municipality['weighted_score'] = calculate_weighted_score(comparison_municipality, weights, filters)
            
            col1, col2, col3 = st.columns([5, 1, 5])
            
            with col1:
                show_single_municipality_details(municipality, images, concept_names, "🏘️ Municipio principal")
                
            with col2:
                st.markdown("<br><br><br>", unsafe_allow_html=True)
                st.markdown("**VS**", unsafe_allow_html=True)
                
            with col3:
                # Header with comparison controls
                comp_header_col1, comp_header_col2 = st.columns([3, 1])
                with comp_header_col1:
                    st.markdown("**🔍 Comparación**")
                with comp_header_col2:
                    end_comparison_key = f"end_comparison_{municipality['NAMEUNIT']}"
                    if st.button("🔄", key=end_comparison_key, help="Terminar comparación"):
                        # Clear comparison state using the same pattern
                        st.session_state.clear_comparison_only = True
                        st.rerun()
                
                show_single_municipality_details(comparison_municipality, images, concept_names, None)
                
                # Comparison dropdown in the right panel
                st.markdown("---")
                st.markdown("**Cambiar municipio:**")
                municipality_options = [f"{row['NAMEUNIT']} (Puntuación: {row['weighted_score']})" 
                                      for _, row in all_municipalities.iterrows() 
                                      if row['NAMEUNIT'] != municipality['NAMEUNIT']]
                
                if municipality_options:
                    # Find current selection
                    current_selection = f"{comparison_municipality['NAMEUNIT']} (Puntuación: {comparison_municipality['weighted_score']})"
                    try:
                        current_index = municipality_options.index(current_selection) + 1
                    except ValueError:
                        current_index = 0
                    
                    selected_comparison = st.selectbox(
                        "Selecciona otro municipio:",
                        ["Selecciona un municipio..."] + municipality_options,
                        index=current_index,
                        key="comparison_selector_in_panel"
                    )
                    
                    if selected_comparison != "Selecciona un municipio..." and selected_comparison != current_selection:
                        # Extract municipality name from the selected option
                        comparison_name = selected_comparison.split(" (Puntuación:")[0]
                        
                        # Automatically update comparison
                        comparison_data = all_municipalities[
                            all_municipalities['NAMEUNIT'] == comparison_name
                        ].iloc[0]
                        st.session_state.comparison_municipality = comparison_data
                        st.rerun()
                    
        else:
            # Show single municipality with comparison option
            show_single_municipality_details(municipality, images, concept_names)
            
            # Comparison functionality
            st.markdown("---")
            st.subheader("🔍 Comparar con otro municipio")
            
            # Create dropdown for municipality selection
            municipality_options = [f"{row['NAMEUNIT']} (Puntuación: {row['weighted_score']})" 
                                  for _, row in all_municipalities.iterrows() 
                                  if row['NAMEUNIT'] != municipality['NAMEUNIT']]
            
            if municipality_options:
                selected_comparison = st.selectbox(
                    "Selecciona municipio para comparar:",
                    ["Selecciona un municipio..."] + municipality_options,
                    key="comparison_selector"
                )
                
                if selected_comparison != "Selecciona un municipio...":
                    # Extract municipality name from the selected option
                    comparison_name = selected_comparison.split(" (Puntuación:")[0]
                    
                    # Automatically start comparison
                    comparison_data = all_municipalities[
                        all_municipalities['NAMEUNIT'] == comparison_name
                    ].iloc[0]
                    st.session_state.comparison_municipality = comparison_data
                    st.rerun()

def show_single_municipality_details(municipality, images, concept_names, title=None):
    """Show details for a single municipality"""
    
    if title:
        st.markdown(f"**{title}**")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Random placeholder image (consistent for each municipality)
        random.seed(hash(municipality['NAMEUNIT']))  # Consistent image per municipality
        img_key = f"placeholder{random.randint(1, 6)}"
        if images[img_key] is not None:
            st.image(images[img_key], caption=municipality['NAMEUNIT'], width=150)
    
    with col2:
        st.markdown(f"**{municipality['NAMEUNIT']}**")
        st.markdown(f'<div class="score-badge">Puntuación: {municipality["weighted_score"]}</div>', unsafe_allow_html=True)
        
        st.markdown(f"👥 **Población:** {municipality['population']:,}")
        st.markdown(f"💰 **Alquiler:** {municipality['rent']}€/mes")
        st.markdown(f"🌡️ **Temp. máx:** {municipality['maxtemp']}°C")
    
    # Accessibility scores
    st.markdown("**Puntuaciones de accesibilidad**")
    
    concepts = ['schools', 'pharmacies', 'hospitals', 'parks', 'cinemas', 'restaurants', 'supermarkets']
    
    for concept in concepts:
        score = municipality[concept]
        icon = get_concept_icon(concept)
        name = concept_names[concept]
        
        col_icon, col_name, col_bar = st.columns([0.3, 1.5, 2])
        
        with col_icon:
            st.markdown(f'<span class="concept-icon">{icon}</span>', unsafe_allow_html=True)
        with col_name:
            st.markdown(f"**{name}**")
        with col_bar:
            # Create colored progress bar based on score
            if score >= 80:
                color = "#28a745"  # Green
            elif score >= 60:
                color = "#ffc107"  # Yellow
            else:
                color = "#dc3545"  # Red
                
            progress_html = f"""
            <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; width: 100%;">
                <div style="background-color: {color}; height: 20px; width: {score}%; border-radius: 10px; 
                           display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
                    {score}/100
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
