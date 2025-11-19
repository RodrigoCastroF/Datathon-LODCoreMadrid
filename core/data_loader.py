# core/data_loader.py
"""Data loading with caching for CSV and shapefiles."""

import os
import warnings
from typing import Tuple, Dict, Optional

import geopandas as gpd
import pandas as pd
import streamlit as st
from PIL import Image


@st.cache_data
def load_data() -> Tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """Load municipality data and geographic boundaries.
    
    Returns:
        Tuple of (municipality_df, merged_geodataframe)
        
    Raises:
        FileNotFoundError: If data files are missing
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    csv_path = os.path.join(parent_dir, "data", "merged_dataset.csv")
    if not os.path.exists(csv_path):
        st.error(f"No se encuentra merged_dataset.csv en {csv_path}")
        st.stop()

    df = pd.read_csv(csv_path)

    shp_path = os.path.join(parent_dir, "boundaries", "recintos_municipales_inspire_peninbal_etrs89.shp")
    if not os.path.exists(shp_path):
        st.error(f"No se encuentra el archivo SHP en {shp_path}")
        st.stop()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gdf = gpd.read_file(shp_path)

    madrid_gdf = gdf[gdf["CODNUT2"] == "ES30"].copy()
    if len(madrid_gdf) == 0:
        st.error("No se encontraron municipios de Madrid en los datos geográficos.")
        st.stop()

    madrid_gdf["NAMEUNIT"] = madrid_gdf["NAMEUNIT"].astype(str)
    df["Nombre"] = df["Nombre"].astype(str)

    merged_gdf = madrid_gdf.merge(df, left_on="NAMEUNIT", right_on="Nombre", how="inner")
    if len(merged_gdf) == 0:
        st.error("No se pudieron combinar los datos geográficos con los datos de merged_dataset.")
        st.write("Ejemplos en CSV:", df["Nombre"].head(10).tolist())
        st.write("Ejemplos en SHP:", madrid_gdf["NAMEUNIT"].head(10).tolist())
        st.stop()

    return df, merged_gdf


@st.cache_data
def load_placeholder_images() -> Dict[str, Optional[Image.Image]]:
    """Load placeholder images for municipalities.
    
    Returns:
        Dictionary mapping image keys to PIL Image objects
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    images: Dict[str, Optional[Image.Image]] = {}
    
    for i in range(1, 7):
        try:
            img_path = os.path.join(parent_dir, "photos", f"placeholder{i}.jpeg")
            img = Image.open(img_path)
            images[f"placeholder{i}"] = img
        except Exception:
            images[f"placeholder{i}"] = None
    
    return images


def get_municipality_image(nombre: str, images_dir: str = "assets/municipalities") -> Optional[Image.Image]:
    """Get real or placeholder image for municipality.
    
    Args:
        nombre: Municipality name
        images_dir: Directory with real images
        
    Returns:
        PIL Image or None
    """
    from pathlib import Path
    import re
    
    def slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[áàäâ]', 'a', text)
        text = re.sub(r'[éèëê]', 'e', text)
        text = re.sub(r'[íìïî]', 'i', text)
        text = re.sub(r'[óòöô]', 'o', text)
        text = re.sub(r'[úùüû]', 'u', text)
        text = re.sub(r'[ñ]', 'n', text)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
    
    script_dir = Path(__file__).parent.parent
    slug = slugify(nombre)
    
    # Try multiple image formats
    for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
        real_img_path = script_dir / images_dir / f"{slug}{ext}"
        if real_img_path.exists():
            try:
                return Image.open(real_img_path)
            except Exception:
                continue
    
    # Fallback to placeholder
    import random
    random.seed(hash(nombre))
    placeholder_num = random.randint(1, 6)
    placeholder_path = script_dir / "photos" / f"placeholder{placeholder_num}.jpeg"
    
    try:
        return Image.open(placeholder_path)
    except Exception:
        return None

